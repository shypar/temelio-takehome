


Decisions
POST /nonprofits
Our endpoint to create nonprofits will accept a list of nonprofits. If the client wants to create a single nonprofit, the payload should be a list of size 1. While we could make our endpoint wrap a single nonprofit in a list, it is best for API endpoints to be consistent for clarity's sake e.g. to have a standard input format

NOTE: What happens if they try to create another? should be idempotent

POST /send_emails
If we receive any emails that are not associated with nonprofits in our existing database, we will indicate that in our response. We will indicate which emails were sent and which were skipped. If all emails are skipped, we will still respond with a 200 response to indicate a valid, well-formed request.

GET /nonprofits
I decided to add an endpoint to get all nonprofits. It just makes sense for the client to see the nonprofits they've added in this email system


