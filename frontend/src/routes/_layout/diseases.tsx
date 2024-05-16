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
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useQuery } from "react-query"

import { type ApiError, DiseasesService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import useCustomToast from "../../hooks/useCustomToast"

export const Route = createFileRoute("/_layout/diseases")({
  component: Diseases,
})

function Diseases() {
  const showToast = useCustomToast()
  const {
    data: diseases,
    isLoading,
    isError,
    error,
  } = useQuery("diseases", () => DiseasesService.readDiseases({}))

  if (isError) {
    const errDetail = (error as ApiError).body?.detail
    showToast("Something went wrong.", `${errDetail}`, "error")
  }

  return (
    <>
      {isLoading ? (
        // TODO: Add skeleton
        <Flex justify="center" align="center" height="100vh" width="full">
          <Spinner size="xl" color="ui.main" />
        </Flex>
      ) : (
        diseases && (
          <Container maxW="full">
            <Heading
              size="lg"
              textAlign={{ base: "center", md: "left" }}
              pt={12}
            >
              Diseases Management
            </Heading>
            <Navbar type={"Disease"} />
            <TableContainer>
              <Table size={{ base: "sm", md: "md" }}>
                <Thead>
                  <Tr>
                    <Th>ID</Th>
                    <Th>Name</Th>
                    <Th>Description</Th>
                    <Th>Healing Steps</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {diseases.data.map((disease) => (
                    <Tr key={disease.id}>
                      <Td>{disease.id}</Td>
                      <Td>{disease.name}</Td>
                      <Td color={!disease.description ? "gray.400" : "inherit"}>
                        {disease.description || "N/A"}
                      </Td>
                      <Td color={!disease.healing_steps ? "gray.400" : "inherit"}>
                        {disease.healing_steps || "N/A"}
                      </Td>
                      <Td>
                        <ActionsMenu type={"Disease"} value={disease} />
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
  )
}

export default Diseases
