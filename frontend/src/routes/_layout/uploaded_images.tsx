import React, { useState } from "react";
import {
  Container,
  Flex,
  Heading,
  Spinner,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  Button,
  Image as ChakraImage,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
} from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { type ApiError, ImagesService } from "../../client";
import useCustomToast from "../../hooks/useCustomToast";
import DiseaseDropdown from "../../components/Diseases/DiseasesDropdown";
import Navbar from "../../components/Common/Navbar";

export const Route = createFileRoute("/_layout/uploaded_images")({
  component: UploadedImages,
});

function UploadedImages() {
  const showToast = useCustomToast();
  const queryClient = useQueryClient();
  const [selectedImage, setSelectedImage] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const { data: imagesData, isLoading, isError, error } = useQuery("images", () =>
    ImagesService.getUploadedImages()
  );

  const changeIsSickMutation = useMutation(
    ({ type, image_id, is_sick_human_input }) =>
      ImagesService.changeIsSick(type, image_id, is_sick_human_input),
    {
      onMutate: async ({ image_id, is_sick_human_input }) => {
        await queryClient.cancelQueries("images");

        const previousImages = queryClient.getQueryData("images");

        queryClient.setQueryData("images", (old) => ({
          ...old,
          data: old.data.map((image) =>
            image.id === image_id ? { ...image, is_sick_human_input } : image
          ),
        }));

        return { previousImages };
      },
      onError: (err, variables, context) => {
        showToast("Error", "Failed to update image.", "error");
        queryClient.setQueryData("images", context.previousImages);
      },
      onSettled: () => {
        queryClient.invalidateQueries("images");
      },
      onSuccess: () => {
        showToast("Success!", "Image updated successfully.", "success");
      },
    }
  );

  const changeDiseaseMutation = useMutation(
    ({ type, image_id, disease_id }) =>
      ImagesService.changeDisease(type, image_id, disease_id),
    {
      onMutate: async ({ image_id, disease_id }) => {
        await queryClient.cancelQueries("images");

        const previousImages = queryClient.getQueryData("images");

        queryClient.setQueryData("images", (old) => ({
          ...old,
          data: old.data.map((image) =>
            image.id === image_id ? { ...image, predicted_disease_human_input: disease_id } : image
          ),
        }));

        return { previousImages };
      },
      onError: (err, variables, context) => {
        showToast("Error", "Failed to update image.", "error");
        queryClient.setQueryData("images", context.previousImages);
      },
      onSettled: () => {
        queryClient.invalidateQueries("images");
      },
      onSuccess: () => {
        showToast("Success!", "Image updated successfully.", "success");
      },
    }
  );

  const handleIsSickChange = (type, image_id, is_sick_human_input) => {
    changeIsSickMutation.mutate({ type, image_id, is_sick_human_input });
  };

  const handleDiseaseChange = (type, image_id, event) => {
    const disease_id = parseInt(event.target.value, 10);
    changeDiseaseMutation.mutate({ type, image_id, disease_id });
  };

  const handleImageClick = (image) => {
    setSelectedImage(image);
    onOpen();
  };

  const images = imagesData ? imagesData.data : [];

  if (isError) {
    const errDetail = (error as ApiError).body?.detail;
    showToast("Something went wrong.", `${errDetail}`, "error");
  }

  return (
    <>
      {isLoading ? (
        <Flex justify="center" align="center" height="100vh" width="full">
          <Spinner size="xl" color="ui.main" />
        </Flex>
      ) : (
        images && (
          <Container maxW="full">
            <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
              Uploaded Images Management
            </Heading>
            <p> These images are uploaded offline </p>
            <Navbar type={"OfflineImage"} />
            <TableContainer>
              <Table size={{ base: "sm", md: "md" }}>
                <Thead>
                  <Tr>
                    <Th>ID</Th>
                    <Th>________ Image ________</Th>
                    <Th>Avg Temperature</Th>
                    <Th>Is Sick</Th>
                    <Th>Is Sick Human Input</Th>
                    <Th>Change Status</Th>
                    <Th>Predicted Disease</Th>
                    <Th>Predicted Disease Human Input</Th>
                    <Th>Change Disease</Th>
                    <Th>Uploaded At</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {images.map((image) => (
                    <Tr key={image.id}>
                      <Td>{image.id}</Td>
                      <Td>
                        <ChakraImage
                          src={image.file_url}
                          alt="Disease"
                          boxSize="150px"
                          objectFit="cover"
                          cursor="pointer"
                          onClick={() => handleImageClick(image)}
                        />
                      </Td>
                      <Td>{image.average_temperature}</Td>
                      <Td>{image.is_sick ? 'Yes' : 'No'}</Td>
                      <Td>{image.is_sick_human_input ? 'Yes' : 'No'}</Td>
                      <Td>
                        <Button
                          colorScheme={image.is_sick_human_input ? "red" : "green"}
                          onClick={() => handleIsSickChange("uploaded", image.id, !image.is_sick_human_input)}
                        >
                          {image.is_sick_human_input ? "Mark as Healthy" : "Mark as Sick"}
                        </Button>
                      </Td>
                      <Td>{image.predicted_disease}</Td>
                      <Td>{image.predicted_disease_human_input}</Td>
                      <Td>
                        <DiseaseDropdown
                          selectedDisease={image.predicted_disease_human_input}
                          onDiseaseChange={(disease_id) =>
                            handleDiseaseChange("uploaded", image.id, { target: { value: disease_id } })
                          }
                        />
                      </Td>
                      <Td>{new Date(image.created_at).toLocaleDateString()}</Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </TableContainer>

            {/* Image Modal */}
            {selectedImage && (
              <Modal isOpen={isOpen} onClose={onClose} size="full">
                <ModalOverlay />
                <ModalContent>
                  <ModalCloseButton />
                  <ModalBody>
                    <img src={selectedImage.file_url} alt="Disease" style={{ width: '100%' }} />
                  </ModalBody>
                </ModalContent>
              </Modal>
            )}
          </Container>
        )
      )}
    </>
  );
}

export default UploadedImages;
