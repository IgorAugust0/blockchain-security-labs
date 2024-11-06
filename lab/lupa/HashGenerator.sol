// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HashGenerator {
    function generateCommitment(uint256 nonce, uint256 bidValue)
        public
        pure
        returns (bytes32)
    {
        return keccak256(abi.encodePacked(nonce, bidValue));
    }
}
