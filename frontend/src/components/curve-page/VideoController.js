import React from "react";

import { 
    Box,
    FormGroup,
    Switch,
    FormControlLabel,
    FormLabel
} from "@mui/material";

const VideoController = props => {
    const { config, onControllerChanged } = props;
    const handleChange = (event) => {
        onControllerChanged({ ...config, [event.target.name]: event.target.checked });
    };
    return <Box m={2}>
        <FormLabel component="legend">Play Video Config</FormLabel>
        <FormGroup row>
            { Object.keys(config).map(name => <FormControlLabel 
                key={name}
                control={<Switch
                    name={name}
                    checked={config[name]} 
                    onChange={handleChange} />} label={name} />) }
        </FormGroup>
    </Box>;
};

export default VideoController;
