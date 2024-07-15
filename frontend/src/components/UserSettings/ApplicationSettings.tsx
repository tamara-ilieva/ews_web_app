import {
  Box,
  Button,
  Container,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Heading,
  Input,
  useColorModeValue,
} from "@chakra-ui/react";
import type React from "react";
import { type SubmitHandler, useForm } from "react-hook-form";
import { useMutation, useQuery } from "react-query";

import { type ApiError, type UpdateDronePictures, DroneService } from "../../client";
import useCustomToast from "../../hooks/useCustomToast";

interface DronePicturesForm extends UpdateDronePictures {
  number: number;
}

const ApplicationSettings: React.FC = () => {
  const color = useColorModeValue("inherit", "ui.white");
  const showToast = useCustomToast();
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<DronePicturesForm>({
    mode: "onBlur",
    criteriaMode: "all",
  });

  const { data, isLoading } = useQuery('drone-pictures', DroneService.getDronePicturesNum, {
    onSuccess: (data) => {
      setValue("number", data.number);
    },
  });

  const updateDronePictures = async (data: UpdateDronePictures) => {
    await DroneService.updateDronePicturesNum({ requestBody: data });
  };

  const mutation = useMutation(updateDronePictures, {
    onSuccess: () => {
      showToast("Success!", "Number of drone pictures updated.", "success");
      reset();
    },
    onError: (err: ApiError) => {
      const errDetail = err.body?.detail;
      showToast("Something went wrong.", `${errDetail}`, "error");
    },
  });

  const onSubmit: SubmitHandler<DronePicturesForm> = async (data) => {
    mutation.mutate({ number: data.number });
  };

  return (
    <>
      <Container maxW="full" as="form" onSubmit={handleSubmit(onSubmit)}>
        <Heading size="sm" py={4}>
          Application Settings
        </Heading>
        <Box w={{ sm: "full", md: "50%" }}>
          <FormControl isRequired isInvalid={!!errors.number}>
            <FormLabel color={color} htmlFor="number">
              Number of Drone Pictures
            </FormLabel>
            <Input
              id="number"
              {...register("number", {
                required: "Number of drone pictures is required",
                valueAsNumber: true,
              })}
              placeholder="Number of Drone Pictures"
              type="number"
              defaultValue={data?.number || ""}
              isLoading={isLoading}
            />
            {errors.number && (
              <FormErrorMessage>
                {errors.number.message}
              </FormErrorMessage>
            )}
          </FormControl>
          <Button
            variant="primary"
            mt={4}
            type="submit"
            isLoading={isSubmitting}
          >
            Save
          </Button>
        </Box>
      </Container>
    </>
  );
};

export default ApplicationSettings;
