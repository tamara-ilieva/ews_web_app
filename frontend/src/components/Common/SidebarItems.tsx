import { Box, Flex, Icon, Text, useColorModeValue } from "@chakra-ui/react"
import { Link } from "@tanstack/react-router"
import type React from "react"
import { FiBriefcase, FiHome, FiSettings, FiUsers } from "react-icons/fi"
import { useQueryClient } from "react-query"

import type { UserOut } from "../../client"

const items = [
  { icon: FiHome, title: "Dashboard", path: "/" },
  // { icon: FiBriefcase, title: "Items", path: "/items" },
  { icon: FiBriefcase, title: "Diseases", path: "/diseases" },
//   { icon: FiBriefcase, title: "Images", path: "/images" },
  { icon: FiBriefcase, title: "Static Images", path: "/static_images" },
  { icon: FiBriefcase, title: "Dynamic Images", path: "/dynamic_images" },
  { icon: FiBriefcase, title: "Uploaded Images", path: "/uploaded_images" },
  { icon: FiSettings, title: "User Settings", path: "/settings" },
]

interface SidebarItemsProps {
  onClose?: () => void
}

const SidebarItems: React.FC<SidebarItemsProps> = ({ onClose }) => {
  const queryClient = useQueryClient()
  const textColor = useColorModeValue("ui.main", "ui.white")
  const bgActive = useColorModeValue("#E2E8F0", "#4A5568")
  const currentUser = queryClient.getQueryData<UserOut>("currentUser")

  const finalItems = currentUser?.is_superuser
    ? [...items, { icon: FiUsers, title: "Team", path: "/admin" }]
    : items

  const listItems = finalItems.map((item) => (
    <Flex
      as={Link}
      to={item.path}
      w="100%"
      p={2}
      key={item.title}
      activeProps={{
        style: {
          background: bgActive,
          borderRadius: "12px",
        },
      }}
      color={textColor}
      onClick={onClose}
    >
      <Icon as={item.icon} alignSelf="center" />
      <Text ml={2}>{item.title}</Text>
    </Flex>
  ))

  return (
    <>
      <Box>{listItems}</Box>
    </>
  )
}

export default SidebarItems
