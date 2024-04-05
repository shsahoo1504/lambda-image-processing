import boto3
from io import BytesIO
from struct import unpack, pack

# Create an SNS client
sns_client = boto3.client('sns')

# SNS topic ARN
sns_topic_arn = 'arn:aws:sns:us-east-1:190345289211:lamda-mail'

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = 'test29032024'
    folder_prefix = 'image/'  # Specify the folder path (prefix)

    # Retrieve object keys within the specified folder
    object_keys = get_object_keys_in_folder(bucket_name, folder_prefix)

    # Process each object within the folder
    for object_key in object_keys:
        # Skip processing if object key ends with '_processed.jpg'
        if object_key.endswith('_processed.jpg'):
            continue
        
        # Download the image file from S3
        image_data = download_image(bucket_name, object_key)
        
        # Process the image (resize and convert to JPEG)
        resized_image_data = process_image(image_data, (100, 100))  # Example: resize to 100x100
        
        # Upload the processed image to S3
        processed_object_key = object_key + '_processed.jpg'
        upload_image(bucket_name, processed_object_key, resized_image_data)
        
        # Mark the original image as processed
        mark_image_as_processed(bucket_name, object_key)
        
        # Send SNS notification
        send_sns_notification(processed_object_key)

    return {
        'statusCode': 200,
        'body': 'Image processing completed successfully'
    }

# Define other functions like get_object_keys_in_folder, download_image, process_image, upload_image, mark_image_as_processed

def send_sns_notification(processed_object_key):
    # Compose the message for the notification
    message = f"Image processed and uploaded to S3: {processed_object_key}"
    
    # Send the message to the SNS topic
    sns_client.publish(TopicArn=sns_topic_arn, Message=message)

def get_object_keys_in_folder(bucket_name, folder_prefix):
    s3 = boto3.client('s3')
    
    # Use list_objects_v2 to list objects within the specified folder prefix
    response = s3.list_objects_v2(
        Bucket=bucket_name,
        Prefix=folder_prefix
    )
    
    # Extract object keys from the response
    object_keys = [obj['Key'] for obj in response.get('Contents', [])]
    
    return object_keys

def download_image(bucket_name, object_key):
    s3 = boto3.client('s3')
    
    # Download the image file from S3
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    image_data = response['Body'].read()
    
    return image_data

def process_image(image_data, size):
    # Example: Resize the image (placeholder for your resizing logic)
    # Here, you can implement your custom resizing algorithm
    # We'll use a basic algorithm that resizes the image by cropping it
    
    # Read the image dimensions from the header
    width, height = unpack('>ii', image_data[16:24])
    
    # Calculate the new dimensions while maintaining aspect ratio
    target_width, target_height = size
    aspect_ratio = width / height
    if aspect_ratio > 1:
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        new_width = int(target_height * aspect_ratio)
        new_height = target_height
    
    # Crop or pad the image to the new dimensions
    resized_image_data = crop_or_pad_image(image_data, (width, height), (new_width, new_height))
    
    return resized_image_data

def crop_or_pad_image(image_data, original_size, new_size):
    original_width, original_height = original_size
    new_width, new_height = new_size
    
    # Calculate the offsets for cropping or padding
    left = (original_width - new_width) // 2
    top = (original_height - new_height) // 2
    
    # Create a new image buffer with the desired size
    output = BytesIO()
    
    # Write the BMP header
    output.write(b'BM')
    output.write(pack('<i', 14 + 40 + new_width * new_height * 3))
    output.write(pack('<H', 0))
    output.write(pack('<H', 0))
    output.write(pack('<I', 14 + 40))
    output.write(pack('<I', 40))
    output.write(pack('<i', new_width))
    output.write(pack('<i', new_height))
    output.write(pack('<H', 1))
    output.write(pack('<H', 24))
    output.write(pack('<I', 0))
    output.write(pack('<I', new_width * new_height * 3))
    output.write(pack('<i', 0))
    output.write(pack('<i', 0))
    output.write(pack('<I', 0))
    output.write(pack('<I', 0))
    
    # Crop or pad the image
    for y in range(new_height):
        for x in range(new_width):
            if (x + left) < original_width and (y + top) < original_height:
                # Copy pixel from original image
                output.write(image_data[14 + 40 + 3 * ((y + top) * original_width + (x + left)):
                                         14 + 40 + 3 * ((y + top) * original_width + (x + left)) + 3])
            else:
                # Pad with white (255, 255, 255) if outside original image bounds
                output.write(b'\xff\xff\xff')
    
    return output.getvalue()

def upload_image(bucket_name, object_key, image_data):
    s3 = boto3.client('s3')
    
    # Upload the processed image to S3
    s3.put_object(Bucket=bucket_name, Key=object_key, Body=image_data)

def mark_image_as_processed(bucket_name, object_key):
    # Rename the original image by appending '_processed' to the key
    new_object_key = object_key + '_processed.jpg'
    
    # Copy the object with the new key to mark it as processed
    s3_client.copy_object(
        Bucket=bucket_name,
        CopySource={'Bucket': bucket_name, 'Key': object_key},
        Key=new_object_key
    )
    
    # Optionally, you can delete the original object if needed
    s3_client.delete_object(Bucket=bucket_name, Key=object_key)
    
def send_sns_notification(processed_object_key):
    # Compose the message for the notification
    message = f"Image processed and uploaded to S3: {processed_object_key}"
    
    # Send the message to the SNS topic
    sns_client.publish(TopicArn=sns_topic_arn, Message=message)
