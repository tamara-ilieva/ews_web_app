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

export const Route = createFileRoute("/_layout/images")({
  component: Images,
});

function Images() {
  const showToast = useCustomToast();
  const {
    data: imagesData,
    isLoading,
    isError,
    error,
  } = useQuery("images", () => ImagesService.getImages());

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
              Image Management
            </Heading>
            <Navbar type={"OfflineImage"} />
            <TableContainer>
              <Table size={{ base: "sm", md: "md" }}>
                <Thead>
                  <Tr>
                    <Th>ID</Th>
                    <Th>Predicted Disease</Th>
                    <Th>Image</Th>
                    <Th>Uploaded At</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {images.map((image) => (
                    <Tr key={image.id}>
                      <Td>{image.id}</Td>
                      <Td>{image.predicted_disease}</Td>
                      <Td>
                        <ChakraImage src={image.file_url} alt="Disease" boxSize="100px" objectFit="cover" />
                      </Td>
                      <Td>{new Date(image.created_at).toLocaleDateString()}</Td>
                      <Td>
                      {<ActionsMenu type={"Image"} value={image} />}

                      </Td>
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

export default Images;
