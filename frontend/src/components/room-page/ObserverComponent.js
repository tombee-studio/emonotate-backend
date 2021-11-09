import React from "react";
import { 
    Avatar, 
    FormControl,
    InputLabel,
    TextField,
    Box,
    Button,
    Grid } from "@material-ui/core";
import PersonIcon from "@material-ui/icons/Person";
import "video.js/dist/video-js.css";
import CurvesListAPI from "../../helper/CurvesListAPI";

class ObserverComponent extends React.Component {
    constructor(props) {
        super(props);
        const { request } = this.props;
        this.request = request;
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
                <FormControl fullWidth sx={{ m: 1 }}>
                    <TextField 
                        id="title" 
                        label="タイトル"
                        margin="normal"
                        value={request.title} />
                    <TextField 
                        id="description" 
                        label="説明"
                        multiline
                        rows={4}
                        margin="normal"
                        value={request.description} />
                </FormControl>
                <Button variant="outlined" onClick={ev => {
                    const api = new CurvesListAPI();
                    api.list({
                        'format': 'json',
                        'search': this.request.room_name,
                    })
                    .then(json => {
                        this.download(json);
                        alert("ダウンロードを終了しました");
                    })
                    .catch(err => {
                        alert(err);
                    });
                }}>ダウンロード</Button>
            </Box>
        );
    }
};

export default ObserverComponent;
