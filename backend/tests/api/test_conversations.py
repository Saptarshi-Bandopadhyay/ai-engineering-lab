async def test_create_conversation(authorized_client):
    response = await authorized_client.post(
        "/api/v1/conversations/", json={"title": "My API Design"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "My API Design"


async def test_cannot_access_other_users_conversation(
    alice_client, bob_conversation_id
):
    # Resource Hiding Verification
    response = await alice_client.get(f"/api/v1/conversations/{bob_conversation_id}")
    assert response.status_code == 404


async def test_cannot_patch_other_users_conversation(alice_client, bob_conversation_id):
    response = await alice_client.patch(
        f"/api/v1/conversations/{bob_conversation_id}", json={"title": "Hacked Title"}
    )
    assert response.status_code == 404


async def test_soft_delete_removes_from_list(authorized_client):
    # 1. Create it
    create_resp = await authorized_client.post(
        "/api/v1/conversations/", json={"title": "To Delete"}
    )
    conv_id = create_resp.json()["id"]

    # 2. Delete it
    delete_resp = await authorized_client.delete(f"/api/v1/conversations/{conv_id}")
    assert delete_resp.status_code == 204

    # 3. Verify it is gone from the list
    list_resp = await authorized_client.get("/api/v1/conversations/")
    assert not any(c["id"] == conv_id for c in list_resp.json())
