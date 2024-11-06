// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

library SimpleCommit {
    enum CommitStatesType { Waiting, Revealed }
    struct CommitType {
        bytes32 commited;
        uint value;
        bool verified;
        CommitStatesType myState;
    }

    function commit(CommitType storage c, bytes32 h) public {
        c.commited = h;
        c.verified = false;
        c.myState = CommitStatesType.Waiting;
    }

    function reveal(CommitType storage c, bytes32 nonce, uint v) public {
        require(c.myState == CommitStatesType.Waiting);
        bytes32 ver = sha256(abi.encodePacked(nonce, v));
        c.myState = CommitStatesType.Revealed;
        if (ver == c.commited) {
            c.verified = true;
            c.value = v;
        }
    }

    function isCorrect(CommitType storage c) public view returns (bool) {
        require(c.myState == CommitStatesType.Revealed, "Wait!");
        return c.verified;
    }

    function getValue(CommitType storage c) public view returns (uint) {
        require(c.myState == CommitStatesType.Revealed);
        require(c.verified == true);
        return c.value;
    }

    function isCommitted(CommitType storage c) public view returns (bool) {
        return c.commited != bytes32(0);
    }
}

// This is just a helper function used in tests, that sits in its own separate file.
// It generates a keccak256 hash for a given nonce and bid value
contract HashGenerator {
    function generateCommitment(uint256 nonce, uint256 bidValue) public pure returns (bytes32) {
        return keccak256(abi.encodePacked(nonce, bidValue));
    }
}
