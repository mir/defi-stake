// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TokenFarm is Ownable {    

    address[] public allowedTokens;
    mapping (address => mapping (address => uint256)) public tokenStakerBalance;
    address[] public stakers;
    mapping(address => uint256) uniqueTokensStaked;
    IERC20 public  dappToken; 
    mapping(address => address) tokenPriceFeedMap; 

    constructor (address _dappTokenAddress) {
        dappToken = IERC20(_dappTokenAddress);
    }

    function setPriceFeedAddress(address _token, address _priceFeed) 
        public onlyOwner {
        tokenPriceFeedMap[_token] = _priceFeed;   
    }

    function stakeToken(uint256 _amount, address _token) public {
        require(_amount > 0, "Number of tokens to stake should be positive");
        require(tokenIsAllowed(_token), "Token is not allowed to stake");
        updateUniqueTokensStake(msg.sender, _token);
        IERC20(_token).transferFrom(msg.sender,address(this),_amount);
        tokenStakerBalance[_token][msg.sender] =
            tokenStakerBalance[_token][msg.sender] + _amount;
        if (uniqueTokensStaked[msg.sender] == 1) {
            stakers.push(msg.sender);
        }
    }

    function unStakeTokens(address _token) public { 
        uint256 balance = tokenStakerBalance[_token][msg.sender];       
        require(tokenIsAllowed(_token), "Token is not allowed to stake");
        require(balance > 0, "Not enough tokens to unstake");        
        tokenStakerBalance[_token][msg.sender] = 0;
        uniqueTokensStaked[msg.sender] = uniqueTokensStaked[msg.sender] - 1;
        IERC20(_token).transferFrom(msg.sender,address(this),balance);
    }

    function updateUniqueTokensStake(address _user, address _token) internal {
        if (tokenStakerBalance[_token][_user] == 0) {
            uniqueTokensStaked[_user] = uniqueTokensStaked[_user] + 1; 
        }
    }

    function issueTokens() public onlyOwner {
        for (uint256 stakerIndex = 0;
            stakerIndex < stakers.length;
            stakerIndex ++) {
            address recepient = stakers[stakerIndex];
            uint256 userTotalValue = getUserTotalValue(recepient);
            dappToken.transfer(recepient,userTotalValue); 
        }
    }    

    function getUserTotalValue(address _user) public view returns(uint256) {
        require(uniqueTokensStaked[_user] > 0, "No tokens staked");
        uint256 totalValue = 0;
        for (uint256  allowedTokensIndex = 0;
            allowedTokensIndex < allowedTokens.length;
            allowedTokensIndex++){
                address _token = allowedTokens[allowedTokensIndex];
                totalValue = totalValue +  getUserSingleTokenValue(_user,_token);
            }
        return totalValue;
    }

    function getUserSingleTokenValue(address _user, address _token)
        public view returns(uint256){
        if (uniqueTokensStaked[_token] <= 0) {
            return 0;
        }
        (uint256 tokenPrice,  uint256 decimals) = getTokenValue(_token);
        return (tokenStakerBalance[_token][_user] * tokenPrice / (10**decimals));
    }

    function getTokenValue(address _token) public view returns(uint256,uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(tokenPriceFeedMap[_token]);
        (,int256 price,,,) = priceFeed.latestRoundData();
        uint256 decimals = uint256(priceFeed.decimals());
        return (uint256(price),decimals);
    }

    function tokenIsAllowed(address _token) public view returns(bool){
        for(uint256 index = 0; index < allowedTokens.length; index++) {
            if (allowedTokens[index] == _token) {
                return true;
            }
        }     
        return false;
    }

    function addAllowedTokens(address _token) public onlyOwner{
         allowedTokens.push(_token);
    }
}