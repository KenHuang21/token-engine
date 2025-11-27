// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

/**
 * @dev Interface of the ERC1400 security token standard.
 */
interface IERC1400 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function balanceOfByPartition(bytes32 partition, address tokenHolder) external view returns (uint256);
    function partitionsOf(address tokenHolder) external view returns (bytes32[] memory);
    function issueByPartition(bytes32 partition, address tokenHolder, uint256 value, bytes calldata data) external;
    function transferByPartition(bytes32 partition, address to, uint256 value, bytes calldata data) external returns (bytes32);
    
    event IssuedByPartition(bytes32 indexed partition, address indexed operator, address indexed to, uint256 value, bytes data, bytes operatorData);
    event TransferByPartition(bytes32 indexed fromPartition, address operator, address indexed from, address indexed to, uint256 value, bytes data, bytes operatorData);
}

/**
 * @dev Contract module which provides a basic access control mechanism, where
 * there is an account (an owner) that can be granted exclusive access to
 * specific functions.
 */
abstract contract Ownable {
    address private _owner;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    constructor(address initialOwner) {
        if (initialOwner == address(0)) {
            _owner = msg.sender;
        } else {
            _owner = initialOwner;
        }
        emit OwnershipTransferred(address(0), _owner);
    }

    modifier onlyOwner() {
        require(owner() == msg.sender, "Ownable: caller is not the owner");
        _;
    }

    function owner() public view virtual returns (address) {
        return _owner;
    }
}

/**
 * @title SimpleERC1400
 * @dev A simplified, gas-optimized ERC1400 implementation for BSC.
 */
contract SimpleERC1400 is IERC1400, Ownable {
    string public name;
    string public symbol;
    uint256 private _totalSupply;

    // Mapping from partition to token holder to balance
    mapping(bytes32 => mapping(address => uint256)) private _balances;
    
    // Mapping from token holder to list of partitions they hold
    mapping(address => bytes32[]) private _partitions;
    
    // Mapping to check if a partition exists for a holder to avoid duplicates in _partitions
    mapping(address => mapping(bytes32 => bool)) private _partitionExists;

    constructor(
        string memory name_,
        string memory symbol_,
        bytes32[] memory partitions_,
        address owner_
    ) Ownable(owner_) {
        name = name_;
        symbol = symbol_;
    }

    function totalSupply() external view override returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) external view override returns (uint256) {
        uint256 total = 0;
        bytes32[] memory userPartitions = _partitions[account];
        for (uint256 i = 0; i < userPartitions.length; i++) {
            total += _balances[userPartitions[i]][account];
        }
        return total;
    }

    function balanceOfByPartition(bytes32 partition, address tokenHolder) external view override returns (uint256) {
        return _balances[partition][tokenHolder];
    }

    function partitionsOf(address tokenHolder) external view override returns (bytes32[] memory) {
        return _partitions[tokenHolder];
    }

    function issueByPartition(
        bytes32 partition,
        address tokenHolder,
        uint256 value,
        bytes calldata data
    ) external override onlyOwner {
        require(tokenHolder != address(0), "Invalid receiver");
        
        _totalSupply += value;
        _balances[partition][tokenHolder] += value;

        if (!_partitionExists[tokenHolder][partition]) {
            _partitions[tokenHolder].push(partition);
            _partitionExists[tokenHolder][partition] = true;
        }

        emit IssuedByPartition(partition, msg.sender, tokenHolder, value, data, "");
    }

    function transferByPartition(
        bytes32 partition,
        address to,
        uint256 value,
        bytes calldata data
    ) external override returns (bytes32) {
        require(to != address(0), "Invalid receiver");
        require(_balances[partition][msg.sender] >= value, "Insufficient balance");

        _balances[partition][msg.sender] -= value;
        _balances[partition][to] += value;

        if (!_partitionExists[to][partition]) {
            _partitions[to].push(partition);
            _partitionExists[to][partition] = true;
        }

        emit TransferByPartition(partition, msg.sender, msg.sender, to, value, data, "");
        return partition;
    }
}
