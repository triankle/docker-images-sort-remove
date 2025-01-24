# docker-images-sort-remove
A short python script which keep X last docker images based on the date( can analyse by microservices)


--> to use the script, be sure to can execute the following command to list docker images ( docker image ls )
--> the script can sort by microservices, the purpose of this script is to remove the older images, but there is an extension for this script, you can choose if yes or not you want to remove the image, the script will also sort by microservice :
example : test/gateway --> 3 images with this name
          test/network --> 4 images with this name
    The script will ask to the user if they want to remove x docker images for the gateway microservice, but also ask another time to remove networks image
