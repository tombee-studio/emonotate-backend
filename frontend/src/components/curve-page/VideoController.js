import React, { useEffect, useState } from "react";

import { 
    Box,
    FormGroup,
    Switch,
    FormControlLabel,
    FormLabel,
    TextField,
    Divider,
    CircularProgress
} from "@mui/material";

import ValueTypeListAPI from "../../helper/ValueTypeListAPI";

const VideoController = props => {
    const { config, onControllerChanged, value_type } = props;
    const [valueType, setValueType] = useState(value_type);
    const [loading, setLoading] = useState(true);
    const handleChange = (event) => {
        onControllerChanged({ ...config, [event.target.name]: event.target.checked });
    };
    const api = new ValueTypeListAPI();
    const title = valueType.title;
    useEffect(() => {
        api.get({
            "search": valueType.title
        }).then(json => {
            if(json.models.length > 0) {
                // TODO: チェックアイコンを表示
                setLoading(false);
            } else {
                // TODO: 新規作成アイコンを表示
            }
        });
    }, []);
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
            }}>
            </TextField>
        </FormGroup>
        {loading && <CircularProgress /> }
    </Box>;
};

export default VideoController;
