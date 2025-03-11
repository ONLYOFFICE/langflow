import React, { forwardRef } from "react";
import SvgOnlyofficeLogo from "./OnlyofficeLogo";

export const OnlyofficeIcon = forwardRef<
  SVGSVGElement,
  React.PropsWithChildren<{}>
>((props, ref) => {
  return <SvgOnlyofficeLogo ref={ref} {...props} />;
});
