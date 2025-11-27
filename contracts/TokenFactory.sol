// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./StandardToken.sol";

contract TokenFactory {
    event TokenCreated(address indexed tokenAddress, string name, string symbol);

    function createToken(
        string memory name,
        string memory symbol,
        uint8 decimals,
        uint256 totalSupply
    ) public returns (address) {
        StandardToken newToken = new StandardToken(name, symbol, decimals, totalSupply);
        // Transfer total supply to the creator (msg.sender)
        newToken.transfer(msg.sender, totalSupply);
        
        emit TokenCreated(address(newToken), name, symbol);
        return address(newToken);
    }
}
