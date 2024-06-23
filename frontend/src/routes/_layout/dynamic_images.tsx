import React, { useState } from 'react';
import { createFileRoute } from "@tanstack/react-router";
import { Container, Flex, Heading, Spinner, Table, TableContainer, Tbody, Td, Th, Thead, Tr, Image as ChakraImage, Button, HStack } from "@chakra-ui/react";
import { useQuery, useMutation, useQueryClient } from "react-query";
import useCustomToast from "../../hooks/useCustomToast";
import ImagesService from '../../client/services/ImagesService';
import ActionsMenu from "../../components/Common/ActionsMenu";
import DiseaseDropdown from "../../components/Diseases/DiseasesDropdown";

export const Route = createFileRoute("/_layout/dynamic_images")({
  component: DynamicImages,
});

function DynamicImages() {
  const showToast = useCustomToast();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const pageSize = 10; // You can also allow this to be dynamic

  const { data: imagesData, isLoading, isError, error } = useQuery(["images", page, pageSize], () => ImagesService.getDynamicImages(page, pageSize));

  const changeIsSickMutation = useMutation(
    ({ type, image_id, is_sick_human_input }) => ImagesService.changeIsSick(type, image_id, is_sick_human_input),
    {
      onMutate: async ({ image_id, is_sick_human_input }) => {
        await queryClient.cancelQueries(["images", page, pageSize]);

        const previousImages = queryClient.getQueryData(["images", page, pageSize]);

        queryClient.setQueryData(["images", page, pageSize], (old) => {
          return {
            ...old,
            data: old.data.map((image) =>
              image.id === image_id ? { ...image, is_sick_human_input: is_sick_human_input } : image
            ),
          };
        });

        return { previousImages };
      },
      onError: (err, variables, context) => {
        showToast("Error", "Failed to update image.", "error");
        queryClient.setQueryData(["images", page, pageSize], context.previousImages);
      },
      onSettled: () => {
        queryClient.invalidateQueries(["images", page, pageSize]);
      },
      onSuccess: () => {
        showToast("Success!", "Image updated successfully.", "success");
      },
    }
  );

  const changeDiseaseMutation = useMutation(
    ({ type, image_id, disease_id }) => ImagesService.changeDisease(type, image_id, disease_id),
    {
      onMutate: async ({ image_id, disease_id }) => {
        await queryClient.cancelQueries(["images", page, pageSize]);

        const previousImages = queryClient.getQueryData(["images", page, pageSize]);

        queryClient.setQueryData(["images", page, pageSize], (old) => {
          return {
            ...old,
            data: old.data.map((image) =>
              image.id === image_id ? { ...image, predicted_disease_human_input: disease_id } : image
            ),
          };
        });

        return { previousImages };
      },
      onError: (err, variables, context) => {
        showToast("Error", "Failed to update image.", "error");
        queryClient.setQueryData(["images", page, pageSize], context.previousImages);
      },
      onSettled: () => {
        queryClient.invalidateQueries(["images", page, pageSize]);
      },
      onSuccess: () => {
        showToast("Success!", "Image updated successfully.", "success");
      },
    }
  );

  const images = imagesData ? imagesData.data : [];

  const handleIsSickChange = (type, image_id, is_sick_human_input) => {
    changeIsSickMutation.mutate({ type, image_id, is_sick_human_input });
  };

  const handleDiseaseChange = (type, image_id, event) => {
    const disease_id = parseInt(event.target.value, 10);
    changeDiseaseMutation.mutate({ type, image_id, disease_id });
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  if (isError) {
    const errDetail = (error).body?.detail;
    showToast("Something went wrong.", `${errDetail}`, "error");
  }

  // Generate page numbers for pagination
  const generatePageNumbers = (currentPage, totalPages) => {
    const delta = 1;
    const range = [];
    for (let i = Math.max(2, currentPage - delta); i <= Math.min(totalPages - 1, currentPage + delta); i++) {
      range.push(i);
    }
    if (currentPage - delta > 2) {
      range.unshift('...');
    }
    if (currentPage + delta < totalPages - 1) {
      range.push('...');
    }
    range.unshift(1);
    if (totalPages > 1) {
      range.push(totalPages);
    }
    return range;
  };

  const pageNumbers = generatePageNumbers(page, imagesData?.total_pages || 0);

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
              Dynamic Image Management
            </Heading>
            <p> These images are taken with the thermal Hikvision camera</p>
            <TableContainer>
              <Table size={{ base: "sm", md: "md" }}>
                <Thead>
                  <Tr>
                    <Th>ID</Th>
                    <Th>Predicted Disease</Th>
                    <Th>Predicted Disease Human Input</Th>
                    <Th>Change Disease</Th>
                    <Th>Is Sick</Th>
                    <Th>Is Sick Human Input</Th>
                    <Th>Change Status</Th>
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
                      <Td>{image.predicted_disease_human_input}</Td>
                      <Td>
                        <DiseaseDropdown
                          selectedDisease={image.predicted_disease_human_input}
                          onDiseaseChange={(disease_id) => handleDiseaseChange("dynamic", image.id, { target: { value: disease_id } })}
                        />
                      </Td>
                      <Td>{image.is_sick ? 'Yes' : 'No'}</Td>
                      <Td>{image.is_sick_human_input ? 'Yes' : 'No'}</Td>
                      <Td>
                        <Button
                          colorScheme={image.is_sick_human_input ? "red" : "green"}
                          onClick={() => handleIsSickChange("dynamic", image.id, !image.is_sick_human_input)}
                        >
                          {image.is_sick_human_input ? "Mark as Healthy" : "Mark as Sick"}
                        </Button>
                      </Td>
                      <Td>
                        <ChakraImage src={image.file_url} alt="Disease" boxSize="100px" objectFit="cover" />
                      </Td>
                      <Td>{new Date(image.created_at).toLocaleDateString()}</Td>
                      <Td>
                        <ActionsMenu type={"Image"} value={image} />
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </TableContainer>
            <Flex justifyContent="center" mt={4}>
              <Button
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 1}
                mr={4}
              >
                Previous
              </Button>
              <HStack spacing={2}>
                {pageNumbers.map((pageNumber, index) =>
                  typeof pageNumber === 'string' ? (
                    <Button key={index} disabled>
                      {pageNumber}
                    </Button>
                  ) : (
                    <Button
                      key={pageNumber}
                      onClick={() => handlePageChange(pageNumber)}
                      colorScheme={page === pageNumber ? "blue" : "gray"}
                    >
                      {pageNumber}
                    </Button>
                  )
                )}
              </HStack>
              <Button
                onClick={() => handlePageChange(page + 1)}
                disabled={page === imagesData.total_pages}
                ml={4}
              >
                Next
              </Button>
            </Flex>
          </Container>
        )
      )}
    </>
  );
}

export default DynamicImages;
