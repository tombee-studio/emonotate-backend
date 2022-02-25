import React, { useState } from "react";

import { 
    Box,
    FormGroup,
    Switch,
    FormControlLabel,
    FormLabel,
    TextField,
    Divider
} from "@mui/material";

const VideoController = props => {
    const { config, onControllerChanged, value_type } = props;
    const [valueType, setValueType] = useState(value_type);
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
        <Divider />
        <FormLabel component="legend">感情曲線の種類</FormLabel>
        <FormGroup row>
            <TextField value={valueType.title} onChange={event => {
                const tmp = {
                    title: event.target.value,
                    axisType: valueType.axisType
                };
                setValueType(tmp);
            }}></TextField>
        </FormGroup>
    </Box>;
};

export default VideoController;
