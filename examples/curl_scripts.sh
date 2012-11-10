# Get Access Token from TaskRabbit:
#DEV
curl -X POST -d @tr_dev_token_post.txt https://taskrabbitdev.com/api/oauth/token -v
#PROD
curl -X POST -d @tr_prod_token_post.txt https://www.taskrabbit.com/api/oauth/token -v

# Create Task with TaskRabbit:
curl -X POST -H "Content-Type: application/json" -H "Authorization: OAuth SSrdla71Z11BA0O2W6vBJZ2JVUmYKWpfIir6SjBi" https://taskrabbitdev.com/api/v1/tasks -v -d @create_post.txt

# Read Task with TaskRabbit:
curl -H "Authorization: OAuth SSrdla71Z11BA0O2W6vBJZ2JVUmYKWpfIir6SjBi" https://taskrabbitdev.com/api/v1/tasks/191 -v 

# Close Task with TaskRabbit:
curl -X POST -H "Authorization: OAuth SSrdla71Z11BA0O2W6vBJZ2JVUmYKWpfIir6SjBi" https://taskrabbitdev.com/api/v1/tasks/191/close -v

# Asana
curl -u GLp1JB6.aRWxlrYAAcPwRkFxtYU5WF2A: https://app.asana.com/api/1.0/users/me
