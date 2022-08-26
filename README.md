# ShiftAdd Design Docs

![Alt text](swagger_page.png "Swagger page")

## Choice of Frameworks:
* I used FastAPI because of its growing popularity, its speed, simplicity and integration with pydantic (coming from Java, I find that the lack of type declaration/validation in Pyton makes me nervous!)
* I used SQLAlchemy because of it's good documentation and ORM pattern, which makes it easy to convert between objects and data row entries
* I used Pytest and Starlette for testing (to be able to create a test client)


## File structure:

* I generally believe that it's important to separate interface from implementation. In development this means that consumers of your APIs can be sure of the same inputs and outputs to expect even if you change the way you compute these values. It's also nice to semantically separate them so your code is more readable, and the complexity is abstracted away.
* Since this is a smaller project, I haven't fully done this since a lot of the implementation didn't take up too many lines of code and were mostly crud operations. Where there were lengthier computations, I separated those out into the "utils.py" file. However, ideally for bigger projects I would have a file something like "api.py" where I would write all the business logic and implementation, then in the main.py file, for each endpoint simply return "api.create_challenge".

## API Design

* I aimed to design the APIs using REST principles and best practices. Generally, these involve some of the following:
  *   Idempotency (multiple identical requests have the same effect as a single call)
  *   Being resource-based and manipulating these resources using representations. With this meaning we should model objects such that the request and response objects are the same for a POST call for example.
  *   Following conventions of URI path naming. For example, using nouns instead of verbs, using plural for collections or array properties
* Some of these APIs don't follow this perfectly - for example, we should disregard the root method, "/", since this is clearly not idempotent and I initially used this trying to test out the HTML Response template. Also, GET "/challenges/current-challenge" also isn't idempotent as this changes after each new challenge is generated. This could be improved potentially by replacing this call instead with "/challenges/{challenge_id}" and use a global variable to keep track of the current challenge_id. However, I decided against this out of the instinct to avoid global variables (risks of unforeseen side effects).
* I did try to organize the API paths such that endpoints sharing the same resource are preceded with "/challenges", "/submissions" But note that for the swagger page I thought to organize them slightly differently e.g. "Statistics" would be all the stats related endpoints, which feels a bit of a clearer semantic distinction in the usage.


## Database:

* I was conscious that the task description stated that persisting state in memory was enough, but I was quite keen to explore how integrating database operations worked in Python and FastAPI - hope that is okay!
* I used SQLAlchemy ORM which has tools to map between objects in code and database tables, which I wanted to try out. It is especially quite neat that you can very easily convert pydantic basemodel classes into a dict and pass that into the SQLAlchemy database model classes.
* For basemodels, originally I was going to make the ChallengeCreate object not have an id required for its instantiation, i.e. the id would be randomly generated after and saved in the Challenge object (you can see this commented out in schemas.py), but I had some difficulty doing this and debugging an issue so I went with generating the id before the resource creation... This probably isn't standard practice though, and if I had more time I would tweak it.  
* With more time I would also be interested in exploring using "relationships" in SQLAlchemy to back populate the challenge objects with a list of submissions. There is a one to many relationship between a challenge and its submissions, so doing this could save us time with querying things like getting all submissions for a challenge. But this is more just exploratory, it really depends on which queries we're trying to optimise for.

## Future improvements:

* I wanted to get the root call to return a html response template (using Jinja2) so I could display some html of the math problem and possibly allow the user to submit via that UI... to start creating some of the front end but I ran out of time to be able to get that working properly
* After some extra consideration, it might have been better to design the database and data models more centered around "Player" objects, rather than "Submission", i.e. have the db store players and then use a PUT call to update the player entry with a new submission/score with every challenge, rather than storing submissions only. This would make retrieving statistics for users a lot more efficient since we would just need to query for the player_id as opposed to filtering the submissions data for all with the specific player_id.
* I didn't finish adding all tests for each API, and if I had more time would finish that off!