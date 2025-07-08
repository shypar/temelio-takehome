from flask import Flask, request, jsonify

app = Flask(__name__)

nonprofits = {}
sent_emails = []

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

    sent, skipped = [], []

    for email in recipients:
        if email in nonprofits:
            rendered_email = template.format(**nonprofits[email])
            print(f"Mock sending to {email}: {rendered_email}")  # Mock email client
            sent_emails.append({
                "to": email,
                "body": rendered_email
            })
            sent.append(email)
        else:
            skipped.append(email)
    
    return jsonify({
        "sent": sent,
        "skipped": skipped
    }), 200

# Get list of sent emails
@app.route('/emails', methods=['GET'])
def get_emails():
    return jsonify(sent_emails), 200

# Get list of nonprofits created
@app.route('/nonprofits', methods=['GET'])
def get_nonprofits():
    return jsonify(list(nonprofits.values())), 200


if __name__ == '__main__':
    app.run(debug=True)