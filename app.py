from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

nonprofits = {}
sent_emails = []
email_drafts = {}

# Create nonprofit(s)
@app.route('/nonprofits', methods=['POST'])
def create_nonprofit():
    data = request.json
    nonprofits_added = 0

    # Verify payload is list of nonprofits
    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of nonprofits"}), 400

    for entry in data:
        email = entry['email']
        if email not in nonprofits:
            nonprofits[email] = {
                "name": entry['name'],
                "address": entry['address'],
                "email": email
            }
            nonprofits_added += 1
    return jsonify({"message": f"{nonprofits_added} nonprofit(s) created"}), 201

# Send emails
@app.route('/send_emails', methods=['POST'])
def send_emails():
    data = request.json
    template = data['template']
    recipients = data['recipients']
    cc_emails = data.get('cc', [])

    sent, skipped = [], []

    for email in recipients:
        if email in nonprofits:
            rendered_email = template.format(**nonprofits[email])
            print(f"Mock sending to {email}: {rendered_email}")  # Mock email client
            sent_emails.append({
                "to": email,
                "cc": cc_emails,
                "body": rendered_email
            })
            sent.append(email)
        else:
            skipped.append(email)
    
    return jsonify({
        "sent": sent,
        "skipped": skipped
    }), 200

# Create email draft
@app.route('/drafts', methods=['POST'])
def create_draft():
    data = request.json
    draft_id = str(uuid.uuid4())

    email_drafts[draft_id] = {
        "template": data["template"],
        "recipients": data["recipients"],
        "cc": data.get("cc", [])
    }

    return jsonify({"draft_id": draft_id}), 201


# Fetch email draft
@app.route('/drafts/<draft_id>', methods=['GET'])
def get_draft(draft_id):
    draft = email_drafts.get(draft_id)
    if not draft:
        return jsonify({"error": "Draft not found"}), 404
    return jsonify(draft), 200


# Edit email draft
@app.route('/drafts/<draft_id>', methods=['PUT'])
def update_draft(draft_id):
    if draft_id not in email_drafts:
        return jsonify({"error": "Draft not found"}), 404

    data = request.json
    email_drafts[draft_id]["template"] = data.get("template", email_drafts[draft_id]["template"])
    email_drafts[draft_id]["recipients"] = data.get("recipients", email_drafts[draft_id]["recipients"])
    email_drafts[draft_id]["cc"] = data.get("cc", email_drafts[draft_id]["cc"])

    return jsonify({"message": "Draft updated"}), 200


# Send email draft
@app.route('/drafts/<draft_id>/send', methods=['POST'])
def send_draft(draft_id):
    draft = email_drafts.get(draft_id)
    if not draft:
        return jsonify({"error": "Draft not found"}), 404

    template = draft["template"]
    recipients = draft["recipients"]
    cc_emails = draft["cc"]

    sent, skipped = [], []

    for email in recipients:
        if email in nonprofits:
            rendered_email = template.format(**nonprofits[email])
            print(f"Mock sending to {email} (CC: {cc_emails}): {rendered_email}")
            sent_emails.append({
                "to": email,
                "cc": cc_emails,
                "body": rendered_email
            })
            sent.append(email)
        else:
            skipped.append(email)

    # Remove draft after sending
    del email_drafts[draft_id]

    return jsonify({
        "sent": sent,
        "skipped": skipped
    }), 200


# Get list of sent emails
@app.route('/emails', methods=['GET'])
def get_emails():
    return jsonify(sent_emails), 200

# Get emails sent to a specific recipient
@app.route('/emails/<email_address>', methods=['GET'])
def get_emails_for_address(email_address):
    filtered_emails = [
        email for email in sent_emails
        if email['to'].lower() == email_address.lower()
    ]
    return jsonify(filtered_emails), 200


# Get list of nonprofits created
@app.route('/nonprofits', methods=['GET'])
def get_nonprofits():
    return jsonify(list(nonprofits.values())), 200


if __name__ == '__main__':
    app.run(debug=True)