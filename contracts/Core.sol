// SPDX-License-Identifier: MIT

pragma solidity ^0.6.0;

contract Core {
    uint256 public pricePerShare;

    constructor(uint256 _pricePerShare) public {
        pricePerShare = _pricePerShare;
    }

    function setPricePerShare(uint256 _pricePerShare) public {
        pricePerShare = _pricePerShare;
    }
}
