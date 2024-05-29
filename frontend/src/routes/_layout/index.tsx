import { Box, Container, Image, SimpleGrid, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useQuery } from "react-query"
import axios from "axios"

import type { UserOut } from "../../client"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const { data, error, isLoading } = useQuery('dashboardImages', fetchDashboardImages)

  if (isLoading) return <Text>Loading...</Text>
  if (error) return <Text>Error loading images</Text>

  return (
    <Container maxW="full">
      <Box pt={12} m={4}>
        <SimpleGrid columns={2} spacing="10px">
          {data?.data.map((item) => (
            <Box key={item.id} borderWidth="1px" borderRadius="lg" overflow="hidden">
              <Image src={item.file_url} alt={`Image ${item.id}`} />
              <Box p="6">
                <Text fontSize="xl">{item.disease || "Нема информации за болест"}</Text>
                <Text fontSize="sm">{new Date(item.created_at).toLocaleString()}</Text>
              </Box>
            </Box>
          ))}
        </SimpleGrid>
      </Box>
    </Container>
  )
}

async function fetchDashboardImages() {
  const { data } = await axios.get('http://localhost:8008/api/v1/ews/dashboard', {
    headers: {
      'accept': 'application/json'
    }
  })
  return data
}

export default Dashboard
