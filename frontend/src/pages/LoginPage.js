import React from "react";
import { Box, Grid } from "@mui/material";
import LoginComponent from "../components/login-page/LoginComponent";

const LoginPage = props => 
    <Grid container alignItems="center" justify="center">
        <Grid item xs={4} />
        <Grid item xs={4}>
            <Box m={2}>
                <LoginComponent />
            </Box>
        </Grid>
        <Grid item xs={4} />
    </Grid>;

export default LoginPage;
