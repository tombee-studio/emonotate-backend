import React from "react";
import { 
    FormControl,
    ButtonGroup,
    FormLabel,
    TextField,
    Box,
    Button,
    Snackbar} from "@material-ui/core";
import "video.js/dist/video-js.css";
import CurvesListAPI from "../../helper/CurvesListAPI";
import RequestListAPI from "../../helper/RequestListAPI"
import EmailAddressList from "./EmailAddressList";

class ObserverComponent extends React.Component {
    constructor(props) {
        super(props);
        const { request } = this.props;
        const useSnackbar = false;
        request.content = request.content.id;
        request.owner = request.owner.id;
        request.value_type = request.value_type.id;
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
            const api = new RequestListAPI();
            const { request } = this.state;
            request.content = request.content.id;
            request.owner = request.owner.id;
            request.value_type = request.value_type.id;
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
                        value={request.title} />
                    <hr />
                    <FormLabel>説明</FormLabel>
                    <TextField 
                        id="description" 
                        multiline
                        rows={4}
                        value={request.description} />
                    <hr />
                    <FormLabel>コンテンツ</FormLabel>
                    <TextField 
                        id="content" 
                        value={request.content}
                        onChange={ev => {
                            const req = this.state.request;
                            req.content = Number(ev.target.value);
                            this.setState({ request: req });
                        }} />
                    <hr />
                    <FormLabel>種類</FormLabel>
                    <TextField 
                        id="value_type" 
                        value={request.value_type} 
                        onChange={ev => {
                            const req = this.state.request;
                            req.value_type = Number(ev.target.value);
                            this.setState({ request: req });
                        }} />
                    <hr />
                    <EmailAddressList 
                        participants={request.participants} 
                        onChangeEmailList={onChangeEmailList} />
                </FormControl>
                <ButtonGroup>
                    <Button variant="outlined" onClick={updateInfo}>更新</Button>
                    <Button variant="outlined" onClick={onClickDownloadButton}>ダウンロード</Button>
                </ButtonGroup>
                <Snackbar
                    open={this.state.useSnackbar}
                    autoHideDuration={3000}
                    onClose={handleClose}
                    message="更新しました"
                />
            </Box>
        );
    }
};

export default ObserverComponent;
