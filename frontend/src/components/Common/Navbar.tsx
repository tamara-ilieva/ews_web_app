import { Button, Flex, Icon, useDisclosure } from "@chakra-ui/react"
import type React from "react"
import { FaPlus } from "react-icons/fa"

import AddUser from "../Admin/AddUser";
import AddItem from "../Items/AddItem";
import AddDisease from "../Diseases/AddDisease";
import AddStaticImage from "../Images/AddStaticImage";

interface NavbarProps {
  type: string
}

const Navbar: React.FC<NavbarProps> = ({ type }) => {
  const addUserModal = useDisclosure()
  const addItemModal = useDisclosure()
  const addDiseaseModal = useDisclosure()
  const addImageModal = useDisclosure()

  let onOpen = addUserModal.onOpen; // default to addUserModal.onOpen

  if (type === "Item") {
    onOpen = addItemModal.onOpen;
  } else if (type === "Disease") {
    onOpen = addDiseaseModal.onOpen;
  } else if (type === "Image"){
    onOpen = addImageModal.onOpen
  }

  return (
    <>
      <Flex py={8} gap={4}>
        <Button
          variant="primary"
          gap={1}
          fontSize={{ base: "sm", md: "inherit" }}
          onClick={onOpen}
        >
          <Icon as={FaPlus} /> Add {type}
        </Button>
        {type === "User" && <AddUser isOpen={addUserModal.isOpen} onClose={addUserModal.onClose} />}
        {type === "Item" && <AddItem isOpen={addItemModal.isOpen} onClose={addItemModal.onClose} />}
        {type === "Disease" && <AddDisease isOpen={addDiseaseModal.isOpen} onClose={addDiseaseModal.onClose} />}
        {type === "Image" && <AddStaticImage isOpen={addImageModal.isOpen} onClose={addImageModal.onClose} />}
      </Flex>
    </>
  )
}

export default Navbar
