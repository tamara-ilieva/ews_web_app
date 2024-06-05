import { Button, Flex, Icon, useDisclosure } from "@chakra-ui/react";
import React from "react";
import { FaPlus } from "react-icons/fa";

import AddUser from "../Admin/AddUser";
import AddItem from "../Items/AddItem";
import AddDisease from "../Diseases/AddDisease";
import AddStaticImage from "../Images/AddStaticImage";
import AddOfflineImage from "../Images/AddOfflineImage";

interface NavbarProps {
  type: string;
}

const Navbar: React.FC<NavbarProps> = ({ type }) => {
  const addUserModal = useDisclosure();
  const addItemModal = useDisclosure();
  const addDiseaseModal = useDisclosure();
  const addStaticImageModal = useDisclosure();
  const addOfflineImageModal = useDisclosure();

  let onOpen;
  let isOpen;
  let onClose;

  switch (type) {
    case "Item":
      onOpen = addItemModal.onOpen;
      isOpen = addItemModal.isOpen;
      onClose = addItemModal.onClose;
      break;
    case "Disease":
      onOpen = addDiseaseModal.onOpen;
      isOpen = addDiseaseModal.isOpen;
      onClose = addDiseaseModal.onClose;
      break;
    case "StaticImage":
      onOpen = addStaticImageModal.onOpen;
      isOpen = addStaticImageModal.isOpen;
      onClose = addStaticImageModal.onClose;
      break;
    case "OfflineImage":
      onOpen = addOfflineImageModal.onOpen;
      isOpen = addOfflineImageModal.isOpen;
      onClose = addOfflineImageModal.onClose;
      break;
    default:
      onOpen = addUserModal.onOpen;
      isOpen = addUserModal.isOpen;
      onClose = addUserModal.onClose;
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
        {type === "User" && <AddUser isOpen={isOpen} onClose={onClose} />}
        {type === "Item" && <AddItem isOpen={isOpen} onClose={onClose} />}
        {type === "Disease" && <AddDisease isOpen={isOpen} onClose={onClose} />}
        {type === "OfflineImage" && <AddOfflineImage isOpen={isOpen} onClose={onClose} />}
        {type === "StaticImage" && <AddStaticImage isOpen={isOpen} onClose={onClose} />}
      </Flex>
    </>
  );
};

export default Navbar;
