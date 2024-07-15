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
  Image as ChakraImage,
} from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "react-query";

import { type ApiError, ImagesService } from "../../client";
import ActionsMenu from "../../components/Common/ActionsMenu";
import Navbar from "../../components/Common/Navbar";
import useCustomToast from "../../hooks/useCustomToast";
import React from "react";

export const Route = createFileRoute("/_layout/uploaded_images")({
  component: UploadedImages,
});

function UploadedImages() {
  const showToast = useCustomToast();
  const {
    data: imagesData,
    isLoading,
    isError,
    error,
  } = useQuery("images", () => ImagesService.getUploadedImages());

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
                          onDiseaseChange={(disease_id) => handleDiseaseChange("dynamic", image.id, { target: { value: disease_id } })}
                        />
                      </Td>
                      <Td>{new Date(image.created_at).toLocaleDateString()}</Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </TableContainer>
          </Container>
        )
      )}
    </>
  );
}

export default UploadedImages;
