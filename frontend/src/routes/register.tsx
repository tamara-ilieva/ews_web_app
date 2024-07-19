import {
  Button,
  Container,
  FormControl,
  FormErrorMessage,
  Heading,
  Input,
  Text,
} from "@chakra-ui/react"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { type SubmitHandler, useForm } from "react-hook-form"
import { useMutation, useQueryClient } from "react-query"

import { UsersService } from "../client" // Updated import path
import { isLoggedIn } from "../hooks/useAuth"
import useCustomToast from "../hooks/useCustomToast"

interface UserCreateForm {
  email: string
  full_name: string
  password: string
  confirm_password: string
}

export const Route = createFileRoute("/register")({
  component: Register,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      })
    }
  },
})

function Register() {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<UserCreateForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      email: "",
      full_name: "",
      password: "",
      confirm_password: "",
    },
  })

  const addUser = async (data: UserCreateForm) => {
    await UsersService.createUser({ requestBody: data })
  }

  const mutation = useMutation(addUser, {
    onSuccess: () => {
      showToast("Success!", "User registered successfully.", "success")
      reset()
      throw redirect({
        to: "/login",
      })
    },
    onError: (err: ApiError) => {
      const errDetail = err.body?.detail
      showToast("Something went wrong.", `${errDetail}`, "error")
    },
    onSettled: () => {
      queryClient.invalidateQueries("users")
    },
  })

  const onSubmit: SubmitHandler<UserCreateForm> = (data) => {
    mutation.mutate(data)
  }

  return (
    <Container
      as="form"
      onSubmit={handleSubmit(onSubmit)}
      h="100vh"
      maxW="sm"
      alignItems="stretch"
      justifyContent="center"
      gap={4}
      centerContent
    >
      <Heading size="xl" color="ui.main" textAlign="center" mb={2}>
        Register
      </Heading>
      <Text align="center">
        Please fill in the form to create a new account.
      </Text>
      <FormControl isInvalid={!!errors.email}>
        <Input
          id="email"
          {...register("email", {
            required: "Email is required",
            pattern: {
              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i,
              message: "Invalid email address",
            },
          })}
          placeholder="Email"
          type="email"
        />
        {errors.email && (
          <FormErrorMessage>{errors.email.message}</FormErrorMessage>
        )}
      </FormControl>
      <FormControl mt={4} isInvalid={!!errors.full_name}>
        <Input
          id="full_name"
          {...register("full_name", {
            required: "Full name is required",
          })}
          placeholder="Full name"
          type="text"
        />
        {errors.full_name && (
          <FormErrorMessage>{errors.full_name.message}</FormErrorMessage>
        )}
      </FormControl>
      <FormControl mt={4} isInvalid={!!errors.password}>
        <Input
          id="password"
          {...register("password", {
            required: "Password is required",
            minLength: {
              value: 8,
              message: "Password must be at least 8 characters",
            },
          })}
          placeholder="Password"
          type="password"
        />
        {errors.password && (
          <FormErrorMessage>{errors.password.message}</FormErrorMessage>
        )}
      </FormControl>
      <FormControl mt={4} isInvalid={!!errors.confirm_password}>
        <Input
          id="confirm_password"
          {...register("confirm_password", {
            required: "Please confirm your password",
            validate: (value) =>
              value === getValues().password || "The passwords do not match",
          })}
          placeholder="Confirm Password"
          type="password"
        />
        {errors.confirm_password && (
          <FormErrorMessage>{errors.confirm_password.message}</FormErrorMessage>
        )}
      </FormControl>
      <Button variant="primary" type="submit" isLoading={isSubmitting} mt={4}>
        Register
      </Button>
    </Container>
  )
}

export default Register
