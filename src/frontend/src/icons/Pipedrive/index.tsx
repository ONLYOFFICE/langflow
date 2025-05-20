import React, { forwardRef } from "react";
import SvgPipedriveIcon from "./PipedriveIcon";

export const PipedriveIcon = forwardRef<SVGSVGElement, React.PropsWithChildren<{}>>(
  (props, ref) => {
    return <SvgPipedriveIcon ref={ref} {...props} />;
  },
);