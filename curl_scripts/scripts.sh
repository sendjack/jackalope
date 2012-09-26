# Get Access Token from TaskRabbit:
curl -X POST -d @token_post.txt https://taskrabbitdev.com/api/oauth/token -v

# Create Task with TaskRabbit:
curl -X POST -H "Content-Type: application/json" -H "Authorization: OAuth SSrdla71Z11BA0O2W6vBJZ2JVUmYKWpfIir6SjBi" https://taskrabbitdev.com/api/v1/tasks -v -d @create_post.txt
