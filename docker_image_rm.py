import subprocess
from datetime import datetime
from collections import defaultdict
import json


def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing the command '{cmd}': {e.stderr}")
        return ""


def get_docker_images():
    """
    Get all Docker images in JSON format.
    """
    cmd = "docker image ls --format 'json'"
    return run_command(cmd).splitlines()


def process_docker_images(limit=3):  # 3 by default
    """
    Identifies microservices, displays the images to keep (most recent ones),
    and deletes the older ones based on user confirmation.
    """
    raw_images = get_docker_images()
    if not raw_images:
        print("No Docker images found.")
        return

    # Group images by microservice
    microservices = defaultdict(list)
    for line in raw_images:
        try:
            image_data = json.loads(line)
            repository = image_data["Repository"]
            tag = image_data["Tag"]
            created_at_str = image_data["CreatedAt"]

            # Convert the creation date to a datetime object
            created_at = datetime.strptime(created_at_str.split(" ")[0], "%Y-%m-%d")

            # Add to the microservice's list
            microservices[repository].append((repository, tag, created_at))
        except (ValueError, KeyError) as e:
            print(f"Error processing line: {line}, error: {e}")

    # Analyze microservices and process images
    for service_name, service_images in microservices.items():
        # Sort images by creation date in descending order
        service_images.sort(key=lambda x: x[2], reverse=True)

        # Keep the 'limit' most recent images
        images_to_keep = service_images[:limit]
        images_to_remove = service_images[limit:]

        # Display results
        print(f"\nMicroservice: {service_name}")
        print(f"  Total number of images: {len(service_images)}")

        print("  Images to keep (most recent):")
        for repo, tag, date in images_to_keep:
            print(f"    {repo}:{tag} - {date}")

        if images_to_remove:
            print("  Images to be removed:")
            for repo, tag, date in images_to_remove:
                print(f"    {repo}:{tag} - {date}")

            # Ask user for confirmation before deletion
            confirm = input(f"Do you want to delete {len(images_to_remove)} old images for '{service_name}'? (y/n): ")
            if confirm.lower() == "y":
                for repo, tag, _ in images_to_remove:
                    delete_docker_image(repo, tag)
        else:
            print("  No images to be removed.")


def delete_docker_image(repository, tag):
    """
    Delete a Docker image using its repository and tag.
    """
    image_name = f"{repository}:{tag}"
    print(f"Deleting image: {image_name}")
    try:
        cmd = f"docker rmi {image_name}"
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Failed to delete image '{image_name}': {e.stderr}")


if __name__ == "__main__":
    try:
        # Ask the user for the limit of images to keep
        limit = int(input("Enter the limit of images to keep per microservice: "))
        process_docker_images(limit=limit)
    except ValueError:
        print("Invalid input, please enter a valid integer.")
