import React from "react";
import { useState } from "react";
import { 
    FormGroup,
    TextField,
    FormHelperText,
    Button,
    Stack,
} from "@mui/material";
import Alert from '@mui/material/Alert';
import IconButton from '@mui/material/IconButton';
import Collapse from '@mui/material/Collapse';
import CloseIcon from '@mui/icons-material/Close';
import SendIcon from '@mui/icons-material/Send';

import AuthenticateAPI from "../../helper/AuthenticateAPI";

const LoginComponent = props => {
    const [open, setOpen] = React.useState(false);
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const loginAction = ev => {
        const api = new AuthenticateAPI()
        const data = {
            username: username,
            password: password
        };
        api.login(data)
            .then(_ => {
                window.location = '/';
            })
            .catch(feedback => {
                setOpen(true);
                setUsername("");
                setPassword("");
            });
    };

    return (
        <FormGroup>
            <Stack direction="column" spacing={1}>
                <Collapse in={open}>
                    <Alert
                        severity="error"
                        action={
                            <IconButton
                            aria-label="close"
                            color="inherit"
                            size="small"
                            onClick={() => {
                                setOpen(false);
                            }}
                            >
                            <CloseIcon fontSize="inherit" />
                            </IconButton>
                        }
                        sx={{ mb: 2 }}>
                        ユーザ名またはパスワードが間違っています
                    </Alert>
                </Collapse>
                <TextField 
                    id="username" 
                    label="ユーザ名" 
                    value={username} 
                    onChange={ev => setUsername(ev.target.value)} />
                <FormHelperText></FormHelperText>
                
                <TextField 
                    id="password" 
                    label="パスワード" 
                    type="password"
                    value={password} 
                    onChange={ev => setPassword(ev.target.value)} />
                <FormHelperText></FormHelperText>
    
                <Button variant="contained" endIcon={<SendIcon />} onClick={loginAction}>
                    LOG IN
                </Button>
            </Stack>
        </FormGroup>
    );
};

export default LoginComponent;
