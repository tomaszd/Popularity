# Popular GitHub Repositories

Design and implement a service checking whether the provided GitHub repository is popular or not.
Here, popular GitHub repository means one for which `score >= 500` where `score = num_stars * 1 + num_forks * 2`.

To retrieve information about a particular repository, use GitHub's official [REST API](https://docs.github.com/en/rest).

Design and implement a RESTful API for this service.

## Non-functional requirements

1. the service should:
   1. use Java 14 with Spring Boot 2 or Python with Django (chosen by you)
   1. be dockerized
   1. use access token to authenticate against GitHub's REST API
   1. respond within 0.5 second
1. the service should include:
   1. Swagger API documentation
   1. health check
1. readme should be replaced with brief notes covering:
   1. service description with all made assumptions
   1. tech stack used (runtime environment, frameworks, key libraries)
   1. how to:
      1. build the service
      1. run automatic tests
      1. run the service locally
   1. what improvements would you make if you had more time

## Evaluation criteria

1. alignment with the requirements
1. usage of best practices when dealing with edge cases that are not covered here
1. code quality and readability
1. presence and quality of (or lack of) automatic tests
1. commit history (thought process, commit messages)

Your work should be handed off in a form of a PR to the private repository that you were given. You are responsible for picking a deadline for its delivery, communicating it and sticking to it.
