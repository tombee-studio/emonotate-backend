import React from "react";
import { 
    FormControl,
    ButtonGroup,
    FormLabel,
    TextField,
    Box,
    Button,
    Snackbar,
    Stack,
    Grid } from "@material-ui/core";
import PersonIcon from "@material-ui/icons/Person";
import "video.js/dist/video-js.css";
import CurvesListAPI from "../../helper/CurvesListAPI";
import RequestListAPI from "../../helper/RequestListAPI"
import EmailAddressList from "./EmailAddressList";

class ObserverComponent extends React.Component {
    constructor(props) {
        super(props);
        const { request } = this.props;
        const useSnackbar = false;
        this.state = { 
            request,
            useSnackbar
        };
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
        const { request } = this.state;
        const onChangeEmailList = (participants) => {
            this.state.request.participants = participants;
        };
        const handleClick = () => {
            this.setState({ useSnackbar: true });
        };
        const handleClose = (event, reason) => {
            if (reason === 'clickaway') return;
            this.setState({ useSnackbar: false });
        };
        const updateInfo = (ev) => {
            const request = this.state.request;
            request.content = request.content.id;
            request.owner = request.owner.id;
            request.value_type = request.value_type.id;
            const api = new RequestListAPI();
            api.update(request.id, request)
                .then(json => {
                    handleClick();
                })
                .catch(err => {
                    alert(err);
                });
        };
        const onClickDownloadButton = (ev) => {
            const api = new CurvesListAPI();
            api.list({
                'format': 'json',
                'search': this.request.room_name,
                'page_size': 200,
            })
            .then(json => {
                this.download(json);
                alert("ダウンロードを終了しました");
            })
            .catch(err => {
                alert(err);
            });
        };
        return (
            <Box m={2}>
                <FormControl fullWidth sx={{ m: 1 }}>
                    <FormLabel>タイトル</FormLabel>
                    <TextField 
                        id="title" 
                        margin="normal"
                        value={request.title} />
                    <FormLabel>説明</FormLabel>
                    <TextField 
                        id="description" 
                        multiline
                        rows={4}
                        margin="normal"
                        value={request.description} />
                    <EmailAddressList 
                        participants={request.participants} 
                        onChangeEmailList={onChangeEmailList} />
                </FormControl>
                <ButtonGroup>
                    <Button variant="outlined" onClick={updateInfo}>
                        更新
                    </Button>
                    <Button variant="outlined" onClick={onClickDownloadButton}>
                        ダウンロード
                    </Button>
                </ButtonGroup>
                <Snackbar
                    open={this.state.useSnackbar}
                    autoHideDuration={6000}
                    onClose={handleClose}
                    message="更新しました"
                />
            </Box>
        );
    }
};

export default ObserverComponent;
