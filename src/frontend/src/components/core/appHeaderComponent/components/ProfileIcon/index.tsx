import { AuthContext } from "@/contexts/authContext";
import { useContext } from "react";

export function ProfileIcon() {
  const { userData } = useContext(AuthContext);

  const profileImageUrl = `${__BASE_URL_API__}files/profile_pictures/${
    userData?.profile_image ?? "Space/046-rocket.svg"
  }`;

  return (
    <img
      src={profileImageUrl}
      className="h-6 w-6 shrink-0 focus-visible:outline-0"
    />
  );
}
