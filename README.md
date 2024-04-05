# Image Processing Lambda Function

This AWS Lambda function is designed to process images stored in an Amazon S3 bucket. It downloads each image, resizes it to a specified size, and then uploads the processed image back to S3. Additionally, it marks the original image as processed and sends a notification to an Amazon SNS topic.

## Prerequisites

Before deploying and running this Lambda function, ensure that you have the following:

- An AWS account with appropriate permissions to create Lambda functions, access S3 buckets, and publish to SNS topics.
- Python 3.x installed on your local development environment.
- `boto3`, `io`, and `struct` Python packages installed. You can install them using pip:


## Deployment

To deploy this Lambda function, follow these steps:

1. Clone this GitHub repository to your local machine:


2. Navigate to the directory containing the code:


3. Edit the `lambda_function.py` file to customize the S3 bucket name, folder prefix, and other parameters as needed.

4. Zip the contents of the directory:


5. Upload the `lambda_function.zip` file to AWS Lambda using the AWS Management Console or AWS CLI.

6. Configure the Lambda function's trigger to be an S3 bucket event for object creation. Follow the instructions below for setting up S3 bucket notification.

7. Create an SNS topic and subscribe to it to receive notifications. Follow the instructions below for creating an SNS topic and subscribing to it.

## Setting up S3 Bucket Notification

1. Go to the Amazon S3 console: [https://console.aws.amazon.com/s3/](https://console.aws.amazon.com/s3/)
2. Select your bucket (`test29032024` in your case).
3. Click on "Properties" tab.
4. Scroll down to the "Event notifications" section and click on "Create event notification".
5. Configure the event notification with the following settings:
- Name: Enter a name for your notification.
- Events: Choose "All object create events".
- Prefix: Enter the folder prefix you want to monitor (e.g., `image/`).
- Suffix: Leave this blank if you want to trigger on all file types.
- Send to: Choose "Lambda function" and select your Lambda function from the dropdown.
6. Click "Save".

## Creating an SNS Topic

1. Go to the Amazon SNS console: [https://console.aws.amazon.com/sns/](https://console.aws.amazon.com/sns/)
2. Click on "Create topic".
3. Enter a name and display name for your topic.
4. Click "Create topic".
5. Once the topic is created, click on the topic ARN to view its details.
6. Copy the ARN of the topic (e.g., `arn:aws:sns:us-east-1:123456789012:MyTopic`).

## Subscribing to the SNS Topic

1. After creating the topic, click on "Create subscription".
2. Choose the protocol for the subscription (e.g., Email).
3. Enter the endpoint for the subscription (e.g., your email address).
4. Click "Create subscription".

## Configuration

Before deploying the Lambda function, ensure that you update the following variables in the `lambda_function.py` file:

- `sns_topic_arn`: The Amazon Resource Name (ARN) of the SNS topic to which notifications will be sent.
- `bucket_name`: The name of the Amazon S3 bucket where the images are stored.
- `folder_prefix`: The prefix of the folder within the S3 bucket where the images are located.

## Usage

Once the Lambda function is deployed and configured, it will automatically process any new images uploaded to the specified S3 bucket folder. The processed images will be resized and saved with the '_processed.jpg' suffix, and notifications will be sent to the specified SNS topic.

