import React from 'react';
import { createFileRoute } from "@tanstack/react-router";
import { Container, Flex, Heading, Spinner, Table, TableContainer, Tbody, Td, Th, Thead, Tr, Image as ChakraImage, Button, Select } from "@chakra-ui/react";
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

  const { data: imagesData, isLoading, isError, error } = useQuery("images", ImagesService.getDynamicImages);

  const changeIsSickMutation = useMutation(
    ({ type, image_id, is_sick_human_input }) => ImagesService.changeIsSick(type, image_id, is_sick_human_input),
    {
      onMutate: async ({ image_id, is_sick_human_input }) => {
        await queryClient.cancelQueries("images");

        const previousImages = queryClient.getQueryData("images");

        queryClient.setQueryData("images", (old) => {
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
    ({ type, image_id, disease_id }) => ImagesService.changeDisease(type, image_id, disease_id),
    {
      onMutate: async ({ image_id, disease_id }) => {
        await queryClient.cancelQueries("images");

        const previousImages = queryClient.getQueryData("images");

        queryClient.setQueryData("images", (old) => {
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

  const images = imagesData ? imagesData.data : [];

  const handleIsSickChange = (type, image_id, is_sick_human_input) => {
    changeIsSickMutation.mutate({ type, image_id, is_sick_human_input });
  };

  const handleDiseaseChange = (type, image_id, event) => {
    const disease_id = parseInt(event.target.value, 10); // Ensure disease_id is an integer
    changeDiseaseMutation.mutate({ type, image_id, disease_id });
  };

  if (isError) {
    const errDetail = (error).body?.detail;
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
              Dynamic Image Management
            </Heading>
            <p> These images are taken with the thermal Optris camera</p>
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
          </Container>
        )
      )}
    </>
  );
}

export default DynamicImages;
