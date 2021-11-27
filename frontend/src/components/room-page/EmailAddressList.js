import React from "react";
import ReactDOM from "react-dom";

import { Box, FormLabel } from "@material-ui/core";

import "./styles.css";

class EmailAddressList extends React.Component {
    state = {
        items: [],
        value: "",
        error: null
    };

    constructor(props) {
        super(props);
        const { participants, onChangeEmailList } = this.props;
        this.state = {
            items: participants || []
        };
        this.onChangeEmailList = onChangeEmailList;
    }

    handleKeyDown = evt => {
        if (["Enter", "Tab", ","].includes(evt.key)) {
            evt.preventDefault();

            var value = this.state.value.trim();

            if (value && this.isValid(value)) {
                const items = [...this.state.items, this.state.value];
                this.setState({
                    items: items,
                    value: ""
                });
                this.onChangeEmailList(items);
            }
        }
    };

    handleChange = evt => {
        this.setState({
            value: evt.target.value,
            error: null
        });
    };

    handleDelete = item => {
        const items = this.state.items.filter(i => i !== item);
        this.setState({
            items: items
        });
        this.onChangeEmailList(this.state.items);
    };

    handlePaste = evt => {
        evt.preventDefault();

        var paste = evt.clipboardData.getData("text");
        var emails = paste.match(/[\w\d\.-]+@[\w\d\.-]+\.[\w\d\.-]+/g);

        if (emails) {
            var toBeAdded = emails.filter(email => !this.isInList(email));
            const items = [...this.state.items, ...toBeAdded];
            this.setState({
                items: items
            });
            this.onChangeEmailList(items);
        }
    };

    isValid(email) {
    let error = null;

    if (this.isInList(email)) {
        error = `${email} has already been added.`;
    }

    if (!this.isEmail(email)) {
        error = `${email} is not a valid email address.`;
    }

    if (error) {
        this.setState({ error });

        return false;
    }

    return true;
    }

    isInList(email) {
        return this.state.items.includes(email);
    }

    isEmail(email) {
        return /[\w\d\.-]+@[\w\d\.-]+\.[\w\d\.-]+/.test(email);
    }

    render() {
        return (
            <Box m={2}>
                <FormLabel>参加者メールリスト</FormLabel>
                <Box m={2}>
                    {this.state.items.map(item => (
                        <div className="tag-item" key={item}>
                        {item}
                        <button
                            type="button"
                            className="button"
                            onClick={() => this.handleDelete(item)}
                        >
                            &times;
                        </button>
                        </div>
                    ))}

                    <input
                        className={"input " + (this.state.error && " has-error")}
                        value={this.state.value}
                        placeholder="Type or paste email addresses and press `Enter`..."
                        onKeyDown={this.handleKeyDown}
                        onChange={this.handleChange}
                        onPaste={this.handlePaste}
                    />

                    {this.state.error && <p className="error">{this.state.error}</p>}
                </Box>
            </Box>
        );
    }
}

export default EmailAddressList;
