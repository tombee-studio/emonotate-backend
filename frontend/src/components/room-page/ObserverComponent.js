import React from "react";
import { 
    Avatar, 
    FormControl,
    InputLabel,
    Input,
    Box,
    Grid } from "@material-ui/core";
import PersonIcon from "@material-ui/icons/Person";
import "video.js/dist/video-js.css";
import CurvesListAPI from "../../helper/CurvesListAPI";

class ObserverComponent extends React.Component {
    constructor(props) {
        super(props);
        const { request } = this.props;
        console.log(request);
    }

    download(exportJson) {
        const fileName = 'finename.json';
        const data = new Blob([JSON.stringify(exportJson)], { type: 'text/json' });
        const jsonURL = window.URL.createObjectURL(data);
        const link = document.createElement('a');
        document.body.appendChild(link);
        link.href = jsonURL;
        link.setAttribute('download', fileName);
        link.click();
        document.body.removeChild(link);
    }

    render() {
        const { request } = this.props;
        return (
            <Box m={2}>
                <FormControl>
                    <InputLabel htmlFor="my-input">説明</InputLabel>
                    <Input id="my-input" aria-describedby="my-helper-text" value={request.description} />
                </FormControl>
            </Box>
        );
    }
};

export default ObserverComponent;
