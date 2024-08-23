---
title: HRMP Channels
description: HRMP channels enable cross-chain communication in Polkadot, a temporary solution before the more efficient XCMP protocol is implemented.
---

# HRMP Channels

## Introduction

Polkadot is designed to enable seamless interoperability between its connected parachains. At the core of this interoperability is the Cross-Consensus Message Format (XCM), a standard language that allows parachains to communicate and interact with each other.

The actual network-layer protocol responsible for delivering XCM-formatted messages between parachains is called the Cross-Chain Message Passing (XCMP) protocol. XCMP maintains messaging queues on the relay chain, serving as a bridge to facilitate cross-chain interactions.

However, as XCMP is still under development, Polkadot has implemented a temporary substitute known as Horizontal Relay-routed Message Passing (HRMP). HRMP provides the same interface and functionality as the planned XCMP, but with a key difference - it stores all messages directly in the relay chain's storage, which is more resource-intensive.

Once XCMP is fully implemented, HRMP will be deprecated in favor of the native XCMP protocol. XCMP will offer a more efficient and scalable solution for cross-chain message passing, as it will not require the relay chain to store all the messages.

## Prerequisites (WIP)

<!-- TODO -->

## Establishing HRMP Channels

To facilitate communication between parachains using the HRMP protocol, the parachains must explicitly establish communication channels by registering them on the relay chain.

Downward and upward channels from and to the relay chain are implicitly available, meaning they do not need to be explicitly opened.

Opening an HRMP channel requires the parachains involved to make a deposit on the relay chain. This deposit covers the expenses of using the relay chain's storage for the message queues associated with the channel.

### Relay Chain Parameters

Each Polkadot relay chain has a set of configurable parameters that control the behavior of the message channels between parachains. These parameters include `hrmpSenderDeposit`, `hrmpRecipientDeposit`, `hrmpChannelMaxMessageSize`, `hrmpChannelMaxCapacity` and more.

When a parachain wants to open a new channel, it must take these parameter values into account to ensure the channel is configured properly.

To view the current values of these parameters in the Polkadot network:

1. Visit [Polkadot.js Apps](https://polkadot.js.org/apps/?rpc=wss%3A%2F%2Fpolkadot.api.onfinality.io%2Fpublic-ws#/explorer), navigate to the **Developer** dropdown and select the **Chain state** option

    ![](/polkadot-ecosystem-docs-draft/images/build-on-polkadot/hrmp-channels/hrmp-channels-1.webp)

2. Under the **configuration** section, call the `activeConfig()` function by clicking the button with the **+** icon. This will display the current settings for all the Polkadot network parameters, including the HRMP channel settings

    ![](/polkadot-ecosystem-docs-draft/images/build-on-polkadot/hrmp-channels/hrmp-channels-2.webp)

### Dispatching Extrinsics

Establishing new HRMP channels between parachains requires dispatching specific extrinsic calls on the Polkadot relay chain from the parachain's origin.

The most straightforward approach is to implement the channel opening logic off-chain, then use the XCM pallet's `send` extrinsic to submit the necessary instructions to the relay chain. However, the ability to send arbitrary programs through the `Transact` instruction in XCM is typically restricted to privileged origins, such as the sudo pallet or governance mechanisms.

Parachain developers have a few options for triggering the required extrinsic calls from their parachain's origin, depending on the configuration and access controls defined:

- Sudo - if the parachain has a sudo pallet configured, the sudo key holder can use the sudo extrinsic to dispatch the necessary channel opening calls
- Governance - the parachain's governance system, such as a council or OpenGov, can be used to authorize the channel opening calls
- Privileged Accounts - the parachain may have other designated privileged accounts that are allowed to dispatch the HRMP channel opening extrinsics

## Opening HRMP Channels Between Parachains

For establishing communication channels between parachains on the Polkadot network, using the HRMP protocol, the following steps are required:

1. Channel request - the parachain that wants to open an HRMP channel must make a request to the parachain it wishes to have an open channel with
2. Channel acceptance - the other parachain must then accept this request in order to complete the channel establishment

This process results in a unidirectional HRMP channel, where messages can flow in only one direction between the two parachains.

To enable bidirectional communication, an additional HRMP channel must be established in the opposite direction. This requires repeating the request and acceptance process, but with the parachains reversing their roles.

Once both unidirectional channels are established, the parachains can then send messages back and forth freely through the bidirectional HRMP communication channel.

### Procedure for Initiating HRMP Channel Setup

This example will demonstrate how to open a channel between parachain 2500 and parachain 2600, using Rococo Local as the relay chain.

#### Step 1 - Fund Sovereign Account {: #init-fund-sovereign-account }
<!-- <a id="init-fund-sovereign-account"></a> -->

The sovereign account for parachain 2500 on the relay chain must be funded so it can take care of any XCM transact fees.

Use Polkadot.js Apps UI to connect to the relay chain and transfer funds from your account to the parachain 2500 sovereign account.
![](/polkadot-ecosystem-docs-draft/images/build-on-polkadot/hrmp-channels/hrmp-channels-3.webp)

??? note "Calculating Parachain Sovereign Account"
    To generate the sovereign account address for a parachain, you'll need to follow these steps:

    1. Determine if the parachain is an "up/down" chain (parent or child) or a "sibling" chain:

        - Up/down chains use the prefix `0x70617261` (which decodes to `b"para"`)

        - Sibling chains use the prefix `0x7369626c` (which decodes to `b"sibl"`)

    2. Calculate the u32 scale encoded value of the parachain ID:
        - Parachain 2500 would be encoded as `c4090000`

    3. Combine the prefix and parachain ID encoding to form the full sovereign account address:

        The sovereign account of parachain 2500 in relay chain will be `0x70617261c4090000000000000000000000000000000000000000000000000000`
        and the SS58 format of this address is `5Ec4AhPSY2GEE4VoHUVheqv5wwq2C1HMKa7c9fVJ1WKivX1Y`
    
    To perform this conversion, you can also use the **"Para ID" to Address** section in [Substrate Utilities](https://www.shawntabrizi.com/substrate-js-utilities/).

#### Step 2 - Create Channel Opening Extrinsic

1. In Polkadot.js Apps, connect to the relay chain, navigate to the **Developer** dropdown and select the **Extrinsics** option

    ![](/polkadot-ecosystem-docs-draft/images/build-on-polkadot/hrmp-channels/hrmp-channels-4.webp)

2. Construct an `hrmpInitOpenChannel` extrinsic call

    1. Select the **hrmp** pallet
    2. Choose the **hrmpInitOpenChannel** extrinsic
    3. Fill in the parameters
        - **recipient** - parachain ID of the target chain (in this case, 2600)
        - **proposedMaxCapacity** - max number of messages that can be pending in the channel at once
        - **proposedMaxMessageSize** - max message size that could be put into the channel
    4. Copy the encoded call data
    ![](/polkadot-ecosystem-docs-draft/images/build-on-polkadot/hrmp-channels/hrmp-channels-5.webp)
    The encoded call data for opening a channel with parachain 2600 is `0x3c00280a00000800000000001000`.

#### Step 3 - Crafting and Submitting the XCM Message {: #init-crafting-and-submitting-the-xcm-message }

To initiate the HRMP channel opening process, you need to create an XCM message that includes the encoded `hrmpInitOpenChannel` call data from the previous step. This message will be sent from your parachain to the relay chain.

This example uses the `sudo` pallet to dispatch the extrinsic. Verify the XCM configuration of the parachain you're working with and ensure you're using an origin with the necessary privileges to execute the `polkadotXcm.send` extrinsic.

The XCM message should contain the following instructions:

- **WithdrawAsset** - withdraws assets from the origin's ownership and places them in the Holding Register
- **BuyExecution** - pays for the execution of the current message using the assets in the Holding Register
- **Transact** - execute the encoded transaction call
- **RefundSurplus** - increases the Refunded Weight Register to the value of the Surplus Weight Register, attempting to reclaim any excess fees paid via BuyExecution
- **DepositAsset** - subtracts assets from the Holding Register and deposits equivalent on-chain assets under the specified beneficiary's ownership

In essence, this process withdraws funds from the parachain's sovereign account to the XCVM Holding Register, then uses these funds to purchase execution time for the XCM Transact instruction, executes Transact, refunds any unused execution time and deposits any remaining funds into a specified account.

To submit the XCM message:

1. Connect to parachain 2500
   
2. Construct the XCM message by filling in all required parameters. Make sure to replace the **call** field with your encoded `hrmpInitOpenChannel` call data from the previous step
   
3. Click the **Submit Transaction** button to dispatch the XCM message to the relay chain.

![](/polkadot-ecosystem-docs-draft/images/build-on-polkadot/hrmp-channels/hrmp-channels-6.webp)

!!! note
    The exact process and parameters for submitting this XCM message may vary depending on your specific parachain and relay chain configurations. Always refer to the most current documentation for your particular network setup.

After submitting the XCM message to initiate the HRMP channel opening, you should verify that the request was successful. Follow these steps to check the status of your channel request:

1. Using Polkadot.js Apps, connect to the relay chain and navigate to the **Developer** dropdown, then select the **Chain state** option

2. Under the **hrmp** section, select the `hrmpOpenChannelRequests` function. Click the button with the **+** icon next to it to call the function. This will display the status of all pending channel requests

If your channel request was successful, you should see an entry for your parachain ID in the list of open channel requests. This confirms that your request has been properly registered on the relay chain and is awaiting acceptance by the target parachain

![](/polkadot-ecosystem-docs-draft/images/build-on-polkadot/hrmp-channels/hrmp-channels-7.webp)

### Procedure for Accepting HRMP Channel

For the channel to be fully established, the target parachain must accept the channel request by submitting an XCM message to the relay chain.

#### Step 1 - Fund Sovereign Account

Before proceeding, ensure that the sovereign account of parachain 2600 on the relay chain is funded. This account will be responsible for covering any XCM transact fees.
To fund the account, follow the same process described in the previous section [Step 1 - Fund Sovereign Account](#init-fund-sovereign-account).

#### Step 2 - Create Channel Opening Extrinsic

1. In Polkadot.js Apps, connect to the relay chain, navigate to the **Developer** dropdown and select the **Extrinsics** option

    ![](/polkadot-ecosystem-docs-draft/images/build-on-polkadot/hrmp-channels/hrmp-channels-4.webp)

2. Construct an `hrmpAcceptOpenChannel` extrinsic call

    1. Select the **hrmp** pallet
    2. Choose the **hrmpAcceptOpenChannel** extrinsic
    3. Fill in the parameters:
        - **sender** - parachain ID of the requesting chain (in this case, 2500)
    4. Copy the encoded call data
    ![](/polkadot-ecosystem-docs-draft/images/build-on-polkadot/hrmp-channels/hrmp-channels-8.webp)
    The encoded call data for accepting a channel with parachain 2500 should be `0x3c01c4090000`

#### Step 3 - Crafting and Submitting the XCM Message

To accept the HRMP channel opening, you need to create and submit an XCM message that includes the encoded `hrmpAcceptOpenChannel` call data from the previous step. This process is similar to the one described in the previous section's [Step 3 - Crafting and Submitting the XCM Message](#init-crafting-and-submitting-the-xcm-message), with a few key differences:
- Use the encoded call data for `hrmpAcceptOpenChannel` obtained in Step 2 of this section
- In the last XCM instruction (DepositAsset), set the beneficiary to parachain 2600's sovereign account to receive any surplus funds

To submit the XCM message:

1. Connect to parachain 2600 using Polkadot.js Apps
2. Construct the XCM message by filling in all required parameters, ensuring you use the correct encoded call data and beneficiary information
3. Submit the transaction to dispatch the XCM message to the relay chain
    ![](/polkadot-ecosystem-docs-draft/images/build-on-polkadot/hrmp-channels/hrmp-channels-9.webp)

After submitting the XCM message to accept the HRMP channel opening, verify that the channel has been set up correctly.

1. Connect to the relay chain using Polkadot.js Apps
2. Navigate to the **Developer** dropdown and select **Chain state**
3. Under the **hrmp** section, query the **hrmpChannels** storage item

If the channel has been successfully established, you should see the channel details in the query results.

![](/polkadot-ecosystem-docs-draft/images/build-on-polkadot/hrmp-channels/hrmp-channels-10.webp)

By following these steps, you will have successfully accepted the HRMP channel request and established a unidirectional channel between the two parachains. 

!!! note
    Remember that for full bidirectional communication, you'll need to repeat this process in the opposite direction, with parachain 2600 initiating a channel request to parachain 2500.
<!-- ## Opening HRMP Channels with System Parachains -->