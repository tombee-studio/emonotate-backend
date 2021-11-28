import React from "react";
import { 
    FormControl,
    FormLabel,
    TextField } from "@material-ui/core";
import "video.js/dist/video-js.css";
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

    setState(state) {
        const { onChange } = this.props;
        onChange(state.request);
        super.setState(state);
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
        return (
            <FormControl fullWidth sx={{ m: 1 }}>
                <FormLabel>タイトル</FormLabel>
                <TextField 
                    id="title" 
                    value={request.title}
                    onChange={ev => {
                        const req = this.state.request;
                        req.title = ev.target.value;
                        this.setState({ request: req });
                    }} />
                <hr />
                <FormLabel>説明</FormLabel>
                <TextField 
                    id="description" 
                    multiline
                    rows={4}
                    value={request.description}
                    onChange={ev => {
                        const req = this.state.request;
                        req.description = ev.target.value;
                        this.setState({ request: req });
                    }} />
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
        );
    }
};

export default ObserverComponent;
