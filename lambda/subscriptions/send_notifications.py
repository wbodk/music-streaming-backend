import json
import boto3
import os
from datetime import datetime

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')

subscriptions_table = dynamodb.Table(os.environ['SUBSCRIPTIONS_TABLE_NAME'])
db_table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    """
    Send email notifications to all subscribers of an artist when they release new content.
    This is triggered when a new song or album is created.
    
    Event format:
    {
        "event_type": "song_created" or "album_created",
        "artist_id": "uuid",
        "content_title": "Song/Album title",
        "content_details": {...}
    }
    """
    try:
        event_type = event.get('event_type')
        artist_id = event.get('artist_id')
        content_title = event.get('content_title')
        
        if not all([event_type, artist_id, content_title]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required event fields'
                })
            }
        
        # Get artist info
        artist_response = db_table.get_item(
            Key={
                'pk': f'ARTIST#{artist_id}',
                'sk': 'METADATA'
            }
        )
        
        if 'Item' not in artist_response:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Artist not found'
                })
            }
        
        artist = artist_response['Item']
        artist_name = artist.get('name', 'Unknown Artist')
        
        # Get all subscriptions for this artist
        subscriptions_response = subscriptions_table.query(
            IndexName='artist-id-index',
            KeyConditionExpression='artist_id = :artist_id',
            ExpressionAttributeValues={
                ':artist_id': artist_id
            }
        )
        
        subscriptions = subscriptions_response.get('Items', [])
        
        if not subscriptions:
            print(f"No subscriptions found for artist {artist_id}")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No subscriptions to notify',
                    'artist_id': artist_id
                })
            }
        
        # Prepare email content
        subject = f"New {event_type.replace('_', ' ').title()} from {artist_name}"
        
        if event_type == 'song_created':
            email_body = generate_song_email(artist_name, content_title, event.get('content_details', {}))
        elif event_type == 'album_created':
            email_body = generate_album_email(artist_name, content_title, event.get('content_details', {}))
        else:
            email_body = f"Your favorite artist {artist_name} has released new content: {content_title}"
        
        # Send emails to all active subscribers
        sent_count = 0
        failed_count = 0
        failed_emails = []
        
        for subscription in subscriptions:
            # Check if notifications are enabled for this subscription
            if not subscription.get('notification_enabled', True):
                print(f"Notifications disabled for user {subscription['user_id']}")
                continue
            
            # Get user email from the subscription record or fetch from Cognito
            user_email = subscription.get('user_email')
            
            if not user_email:
                print(f"No email found for user {subscription['user_id']}")
                failed_count += 1
                failed_emails.append(subscription['user_id'])
                continue
            
            try:
                # Send email via SES
                ses.send_email(
                    Source=os.environ.get('SES_SENDER_EMAIL', 'noreply@musicstreaming.local'),
                    Destination={
                        'ToAddresses': [user_email]
                    },
                    Message={
                        'Subject': {
                            'Data': subject,
                            'Charset': 'UTF-8'
                        },
                        'Body': {
                            'Html': {
                                'Data': email_body,
                                'Charset': 'UTF-8'
                            }
                        }
                    }
                )
                sent_count += 1
                print(f"Email sent to {user_email}")
            except Exception as e:
                print(f"Failed to send email to {user_email}: {str(e)}")
                failed_count += 1
                failed_emails.append(user_email)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Notification sending completed',
                'event_type': event_type,
                'artist_id': artist_id,
                'artist_name': artist_name,
                'total_subscribers': len(subscriptions),
                'emails_sent': sent_count,
                'emails_failed': failed_count,
                'failed_recipients': failed_emails
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error sending notifications',
                'message': str(e)
            })
        }


def generate_song_email(artist_name, song_title, details):
    """Generate HTML email for new song notification"""
    genre = details.get('genre', 'Music')
    album_title = details.get('album_title', 'Unknown Album')
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            .header {{ background-color: #6366f1; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f3f4f6; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
            .cta-button {{ display: inline-block; background-color: #6366f1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎵 New Music Release!</h1>
            </div>
            <div class="content">
                <p>Hi there!</p>
                <p><strong>{artist_name}</strong> has just released a new song that you might love:</p>
                <h2>{song_title}</h2>
                <p><strong>Album:</strong> {album_title}</p>
                <p><strong>Genre:</strong> {genre}</p>
                <p>Head over to our app to listen to this amazing new track!</p>
                <a href="{os.environ.get('APP_URL', 'https://musicstreaming.local')}/songs" class="cta-button">Listen Now</a>
            </div>
            <div class="footer">
                <p>You're receiving this email because you're subscribed to {artist_name}.</p>
                <p><a href="{os.environ.get('APP_URL', 'https://musicstreaming.local')}/settings">Manage your notifications</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def generate_album_email(artist_name, album_title, details):
    """Generate HTML email for new album notification"""
    release_date = details.get('release_date', 'Now')
    genre = details.get('genre', 'Music')
    song_count = details.get('total_songs', 'Multiple')
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            .header {{ background-color: #6366f1; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f3f4f6; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
            .cta-button {{ display: inline-block; background-color: #6366f1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💿 New Album Release!</h1>
            </div>
            <div class="content">
                <p>Hi there!</p>
                <p><strong>{artist_name}</strong> has just released a new album that you might love:</p>
                <h2>{album_title}</h2>
                <p><strong>Released:</strong> {release_date}</p>
                <p><strong>Genre:</strong> {genre}</p>
                <p><strong>Tracks:</strong> {song_count}</p>
                <p>Explore the entire album on our platform!</p>
                <a href="{os.environ.get('APP_URL', 'https://musicstreaming.local')}/albums" class="cta-button">Explore Album</a>
            </div>
            <div class="footer">
                <p>You're receiving this email because you're subscribed to {artist_name}.</p>
                <p><a href="{os.environ.get('APP_URL', 'https://musicstreaming.local')}/settings">Manage your notifications</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html
