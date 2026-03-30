from database import create_user

print("Creating test user...")
user_id = create_user("testuser", "test@example.com", "testpass123", "Test User")
print("Test user created!")
print("Login with: test@example.com / testpass123")