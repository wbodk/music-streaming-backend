# AWS SES Configuration Guide

## Prerequisites

- AWS CLI installed and configured
- Appropriate AWS IAM permissions for SES and Lambda

---

## Step-by-Step Setup

### 1. Verify Email Address in SES

First, verify the sender email address with AWS SES:

```bash
# Verify the sender email
aws ses verify-email-identity \
  --email-address noreply@musicstreaming.local \
  --region eu-west-3
```

Output:
```json
{
  "VerificationAttributes": {
    "noreply@musicstreaming.local": {
      "VerificationStatus": "Pending",
      "VerificationToken": "..."
    }
  }
}
```

**Note:** You'll receive a verification email at this address. Click the link to confirm.

### 2. Check Verification Status

```bash
aws ses list-verified-email-addresses --region eu-west-3
```

Output (once verified):
```json
{
  "VerifiedEmailAddresses": [
    "noreply@musicstreaming.local"
  ]
}
```

---

### 3. Update Lambda Environment Variables

In `music_streaming_backend/lambda_stack.py`, ensure these are configured:

```python
environment={
    "SUBSCRIPTIONS_TABLE_NAME": subscriptions_table.table_name,
    "TABLE_NAME": db.table_name,
    "SES_SENDER_EMAIL": "noreply@musicstreaming.local",  # CHANGE THIS
    "APP_URL": "https://musicstreaming.local"             # CHANGE THIS
}
```

---

### 4. Configure IAM Permissions

The Lambda function needs SES permissions. Already added in `lambda_stack.py`:

```python
self.send_notifications_handler.add_to_role_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=[
            "ses:SendEmail",
            "ses:SendRawEmail"
        ],
        resources=["*"]
    )
)
```

---

### 5. Request Production Access (Recommended)

By default, SES operates in **Sandbox Mode**. In sandbox mode:
- ✅ Can send from verified addresses
- ✅ Can send to verified addresses
- ❌ Cannot send to arbitrary addresses

To remove sandbox limitations:

1. Go to AWS SES Console: https://console.aws.amazon.com/ses/
2. Select your region (eu-west-3)
3. Click "Account Dashboard" in the left menu
4. Click "Request Production Access"
5. Fill the form with your use case
6. Wait for approval (usually 24 hours)

### 6. Set Up Email Receiving (Optional)

To handle bounces and complaints:

```bash
aws ses set-identity-notification-topic \
  --identity noreply@musicstreaming.local \
  --notification-type Bounce \
  --sns-topic arn:aws:sns:eu-west-3:ACCOUNT_ID:email-bounces \
  --region eu-west-3
```

---

## Testing Email Sending

### Test 1: Send Test Email via AWS CLI

```bash
aws ses send-email \
  --source noreply@musicstreaming.local \
  --destination ToAddresses=your-email@example.com \
  --message "Subject={Data='Test Email'},Body={Html={Data='<h1>Test</h1><p>This is a test email.</p>'}}" \
  --region eu-west-3
```

### Test 2: Subscribe and Create Content

```bash
# 1. Subscribe user to artist
curl -X POST https://api.musicstreaming.com/users/user-123/subscriptions/artist-456 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"user_email": "your-email@example.com"}'

# 2. Create a new song (as admin)
curl -X POST https://api.musicstreaming.com/songs \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Song",
    "artist_id": "artist-456",
    "album_id": "album-789",
    "duration": 180,
    "genre": "Pop"
  }'

# 3. Check email inbox for notification
```

### Test 3: Monitor in CloudWatch

```bash
# View Lambda logs
aws logs tail /aws/lambda/send-notifications --follow --region eu-west-3

# Get recent errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/send-notifications \
  --filter-pattern "ERROR" \
  --region eu-west-3
```

---

## Environment Variables Configuration

### Production Configuration

Update these in `lambda_stack.py` for production:

```python
environment={
    "SUBSCRIPTIONS_TABLE_NAME": subscriptions_table.table_name,
    "TABLE_NAME": db.table_name,
    "SES_SENDER_EMAIL": "notifications@yourdomain.com",
    "APP_URL": "https://musicstreaming.yourdomain.com",
    "AWS_REGION": "eu-west-3"
}
```

### Custom Domain Email

If using a custom domain:

1. Verify domain with SES:
```bash
aws ses verify-domain-identity \
  --domain yourdomain.com \
  --region eu-west-3
```

2. Add DKIM records to domain DNS (follow AWS instructions)

3. Update SES_SENDER_EMAIL to: `notifications@yourdomain.com`

---

## Monitoring & Troubleshooting

### Check SES Quota

```bash
aws ses get-account-sending-enabled --region eu-west-3
aws ses get-send-statistics --region eu-west-3
```

### View Sending History

```bash
aws logs describe-log-streams \
  --log-group-name /aws/lambda/send-notifications \
  --region eu-west-3
```

### Common Issues

| Issue | Solution |
|-------|----------|
| MessageRejected | Email not verified in SES |
| InvalidParameterValue | Sender email format invalid |
| Throttling | Too many emails at once (rate limit) |
| ServiceUnavailable | SES temporary issue |

---

## Rate Limiting

SES default quota:
- **Sending rate**: 14 emails per second
- **Daily quota**: 50,000 emails per day

To increase:
1. Go to SES Dashboard
2. Select "Sending Limits"
3. Click "Request a Sending Limit Increase"
4. Follow the form

---

## Best Practices

✅ Use verified sender email
✅ Monitor bounce and complaint rates
✅ Implement unsubscribe mechanism
✅ Handle soft and hard bounces
✅ Keep email templates professional
✅ Test in sandbox mode first
✅ Request production access before launch
✅ Use domain authentication (DKIM/SPF)
✅ Monitor SES sending statistics
✅ Set up CloudWatch alarms

---

## Deployment Commands

```bash
# Validate the stack
cdk synth

# Deploy the updated stack
cdk deploy

# Monitor deployment
aws cloudformation describe-stacks \
  --stack-name MusicStreamingLambdaStack \
  --region eu-west-3
```

---

## Cleanup (if needed)

```bash
# Remove Lambda
cdk destroy --force

# Delete verified email
aws ses delete-identity \
  --identity noreply@musicstreaming.local \
  --region eu-west-3
```

---

## Support Resources

- [AWS SES Documentation](https://docs.aws.amazon.com/ses/)
- [SES FAQs](https://docs.aws.amazon.com/ses/latest/dg/ses-faq.html)
- [Email Best Practices](https://docs.aws.amazon.com/ses/latest/dg/best-practices-email.html)
