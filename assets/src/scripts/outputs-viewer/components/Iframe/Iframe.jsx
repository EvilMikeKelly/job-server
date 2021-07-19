import PropTypes from "prop-types";
import React, { useLayoutEffect, useState } from "react";
import useWindowSize from "../../hooks/useWindowSize";

function Iframe({ data, file }) {
  const windowSize = useWindowSize();
  const [frameHeight, setFrameHeight] = useState("");
  const id = encodeURIComponent(file.url).replace(/\W/g, "");

  useLayoutEffect(() => {
    setFrameHeight(
      window.innerHeight -
        document.getElementById(id).getBoundingClientRect().top -
        58 // Magic number…
    );
  }, [windowSize, id]);

  return (
    <iframe
      frameBorder="0"
      height={frameHeight}
      id={id}
      src={file.url}
      srcDoc={data}
      title={file.name}
      width="100%"
    />
  );
}

Iframe.propTypes = {
  data: PropTypes.string.isRequired,
  file: PropTypes.shape({
    name: PropTypes.string,
    url: PropTypes.string,
  }).isRequired,
};

export default Iframe;
