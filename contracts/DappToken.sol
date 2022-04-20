// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract DappToken is ERC20 {
    constructor(uint256 initialSupply) ERC20("DappToken", "DappTKN") {
        _mint(msg.sender, 1e6*1e18);
    }
}