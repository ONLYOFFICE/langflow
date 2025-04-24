import React, { forwardRef } from "react";
import SvgZoomIcon from "./ZoomIcon";

export const ZoomIcon = forwardRef<SVGSVGElement, React.PropsWithChildren<{}>>(
  (props, ref) => {
    return <SvgZoomIcon ref={ref} {...props} />;
  },
);