from pytezos import pytezos
from tkinter import *
from ttkthemes import ThemedTk
from tkinter import ttk, font
from tkinter.ttk import *
from PIL import ImageTk, Image

window = ThemedTk(theme='breeze')   

window.title('PyTezos SmartContract Interacter')

window.attributes('-zoomed', True)

# initalizing height and width of the window
window_height = window.winfo_screenheight()
window_width = window.winfo_screenwidth()

global_public_hash = None
global_private_hash = None
pytezos_inst = None
contract_inst = None
network_url = None
wallet_address = None

root_top_frame = ttk.Frame(window)

# widget functions ------------------

def open_img(root: Frame, path: str, cord_x: int, cord_y: int, dimensions: tuple):
    global img
    img = ImageTk.PhotoImage(Image.open(path).resize((dimensions[0], dimensions[1])))
    panel = Label(root, image=img)
    panel.grid(rowspan=3, column=cord_y)


def show_warning(window_obj: ThemedTk, duration: int, label: str):
     popup = Toplevel(window_obj)
     popup.geometry(f'800x100+{int(window_width/2)-500}+{int(window_height/2)-100}')
     warning_label = Label(popup, text=label, font="Ariel, 20")
     warning_label.grid()
     popup.after(duration, lambda:popup.destroy())
     popup.mainloop()

def clear_contents(frame_obj: Frame):
    frame_obj.destroy()

def destroy_msg_and_refresh_table(canvas_ref: Canvas, popup: Toplevel, entrypoints: dict, index: int, value: str):
    enum_obj = list(enumerate(entrypoints))

    entrypoint = enum_obj[index][1]
    datatype = entrypoints[entrypoint]

    if str(datatype)[36:-2] == 'IntType':
        value = int(value)
    elif str(datatype)[36:-2] == 'NoneType':
        private_smartcontract_inst = pytezos.contract(global_private_hash)
        obj = getattr(private_smartcontract_inst, entrypoint)
        obj.__call__().as_transaction().send()
        popup.destroy()
        show_contract_details(canvas_ref)
        return
        
   # making the entrypoint call

    pytezos_inst = pytezos.using(shell=network_url, key=global_private_hash)
    contract_inst = pytezos_inst.contract(global_public_hash)
    obj = getattr(contract_inst, entrypoint)
    obj.__call__(value).as_transaction().send()
    popup.destroy()
    show_contract_details(frame_obj=canvas_ref, public_hash=global_public_hash, private_hash=global_private_hash)

def double_click(tree: ttk.Treeview, event, canvas_ref: Canvas, entrypoints: dict):
    index = tree.identify('item', event.x, event.y)

    if global_private_hash != '':
        msg_box = Toplevel(window)
        msg_box.geometry(f'800x180+{int(window_width/2)-200}+{int(window_height/2)-100}')

        label = ttk.Label(msg_box, text="Enter the parameter: ", font=("Ariel, 22"))
        label.grid(row=0, column=0)

        input = ttk.Entry(msg_box, width=45)
        input.grid(row=0, column=1)

        input.bind("<Return>", lambda a: destroy_msg_and_refresh_table(canvas_ref=canvas_ref, popup=msg_box, entrypoints=entrypoints, index=int(index), value=input.get().strip()))

        btn = ttk.Button(msg_box, text='Run', command=lambda: destroy_msg_and_refresh_table(canvas_ref=canvas_ref, popup=msg_box, entrypoints=entrypoints, index=int(index), value=input.get().strip()))

        btn.grid(row=1, columnspan=2, pady=30)

        msg_box.mainloop()
    else:
        msg_box = Toplevel(window)
        msg_box.geometry(f'800x180+{int(window_width/2)-200}+{int(window_height/2)-100}')

        label = ttk.Label(msg_box, text="Please enter the private hash of your account\nto call the entrypoint", font=("Ariel, 22"))
        label.grid(row=0, column=0)

        msg_box.mainloop()

def delete_canvas(canvas_ref: Canvas):
    canvas_ref.destroy()

    ## creating the bottom frame again
    bottom_frame = ttk.Frame(window)

    contract_add_label_public = ttk.Label(bottom_frame, text="Enter public hash of contract: ", font=("Ariel, 20"), justify='left')

    contract_add_label_public.grid(row=5, column=0, pady=20, padx=20, sticky=W)

    contract_add_input_public = ttk.Entry(bottom_frame, width=90, justify='center', font=("DejaVu Sans Mono", 13))

    contract_add_input_public.grid(row=5, column=1)

    contract_add_label_private = ttk.Label(bottom_frame, text="Enter private hash of contract(optional): ", font=("Ariel, 20"), justify='left')

    contract_add_label_private.grid(row=6, column=0, pady=20, padx=20, sticky=W)

    contract_add_input_private = ttk.Entry(bottom_frame, width=90, justify='center', font=("DejaVu Sans Mono", 13))

    contract_add_input_private.grid(row=6, column=1)

    button_style = ttk.Style()
    button_style.configure('W.TButton', font= ('Arial', 17))
    submit_contract = ttk.Button(bottom_frame, text="Connect", width=30, style='W.TButton', command=lambda: show_contract_details(bottom_frame, public_hash=contract_add_input_public.get(), private_hash=contract_add_input_private.get(), ))

    submit_contract.grid(row=7, columnspan=2,  pady=20)

    bottom_frame.grid(row=5, column=0)


def show_contract_details(frame_obj: Frame, public_hash: str, private_hash: str):
    global global_public_hash, global_private_hash, contract_inst

    if public_hash == '':
        show_warning(window_obj=window, duration=3000, label='Please enter a public hash')
        return
    
    try:
        pytezos_inst = pytezos.using(shell=network_url, key=wallet_address)
        contract_inst = pytezos_inst.contract(public_hash)

        entrypoint_dict = dict(contract_inst.entrypoints)
        
        entrypoint_dict.pop('default')
        storage_dict = contract_inst.storage()
    except:
        show_warning(window_obj=window, duration=11000, label='Something went wrong while connecting the contract...')
        return

    global_public_hash = public_hash
    global_private_hash = private_hash
    clear_contents(frame_obj=frame_obj)

    canvas = Canvas(window)
    
    button_style = Style()
    button_style.configure('W.TButton', font= ('Arial', 17))

    back_btn = ttk.Button(canvas, text='Go Back', style="W.TButton",command=lambda: delete_canvas(canvas_ref=canvas))
    back_btn.grid(row=8, column=0, pady=20)

    refresh_btn = ttk.Button(canvas, text='Refresh', style="W.TButton", command=lambda: show_contract_details(frame_obj=canvas, public_hash=global_public_hash, private_hash=global_private_hash))
    refresh_btn.grid(row=8, column=1, pady=20, padx=10)

    label = ttk.Label(canvas, text='Double click the entrypoint to run it!', font=("Ariel", 17))
    label.grid(row=8, column=2, pady=20)

    yscrollbar = ttk.Scrollbar(canvas, orient='vertical')

    style = ttk.Style()
    style.configure("mystyle.Treeview", font=("Ariel", 13))
    style.configure("mystyle.Treeview.Heading", font=("Ariel", 17))
    style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

    tree = ttk.Treeview(canvas, yscrollcommand=yscrollbar.set, column=("c1", "c2", "c3", "c4"), height=15, style="mystyle.Treeview")
    
    tree.grid(row=9, column=0, rowspan=len(entrypoint_dict.keys()), columnspan=4, padx=30)

    tree.column("#0", width=70, anchor=W, stretch=YES)
    tree.column("#1", width=400, anchor=W, stretch=YES)
    tree.column("#2", width=400, anchor=W, stretch=YES)
    tree.column("#3", width=400, anchor=W, stretch=YES)

    tree.heading("#0", text="S.No")
    tree.heading("#1", text="Entrypoint name")
    tree.heading("#2", text="Default value")
    tree.heading("#3", text="Parameter type")

    ind=0
    for key1, key2 in zip(entrypoint_dict.keys(), storage_dict.keys()):
        tree.insert(parent='', index=ind, iid=ind, values=(key1, storage_dict[key2], str(entrypoint_dict[key1])[36:-2]), text=f"{ind+1}")
        ind += 1

    tree.bind("<Double-1>", lambda event: double_click(tree, event, canvas, entrypoint_dict))

    yscrollbar.configure(command=tree.yview)
    yscrollbar.grid(row=9, column=3, rowspan=len(entrypoint_dict.keys()), sticky=NS)

    canvas.grid()
    

def create_wallet_screen(wallet_address: str, network: str):
    label = ttk.Label(window, text='Your Wallet Details', font=("Ariel", 50, "bold underline"))
    label.grid(row=0, column=0, padx=10, pady=(10, 10), sticky=W)

    left_wallet_frame = ttk.Frame(window)

    tez_coins = float(pytezos_inst.balance())
   
    address_label = ttk.Label(left_wallet_frame, text=f"Wallet Address: {wallet_address}", font=("Ariel, 20"))

    address_label.grid(row=1, column=0, pady=(100,0),sticky=W)

    network_label = ttk.Label(left_wallet_frame, text=f"Wallet Network: {network.upper()}", font=("Ariel, 20"))

    network_label.grid(row=2, column=0, pady=(20,20),sticky=W)

    tez_coins = float(pytezos_inst.balance())
    tez_coins_label = ttk.Label(left_wallet_frame, text=f"TEZ coins: {tez_coins} ~ {round(tez_coins*1.12,3)}$", font=("Ariel, 20"))

    tez_coins_label.grid(row=3, column=0,sticky=W)

    left_wallet_frame.grid(row=1, column=0)

    right_wallet_frame = ttk.Frame(window)

    open_img(right_wallet_frame, "tezos_logo.png", 1, 0, (250,250))

    right_wallet_frame.grid(row=1, column=1, sticky=W)

    label = ttk.Label(window, text='SmartContract Details', font=("Ariel", 50, "bold underline"))
    label.grid(row=4, column=0, sticky=W, pady=(30,20), padx=10)

    ####
    bottom_frame = ttk.Frame(window)

    contract_add_label_public = ttk.Label(bottom_frame, text="Enter public hash of contract: ", font=("Ariel, 20"), justify='left')

    contract_add_label_public.grid(row=5, column=0, pady=20, padx=20, sticky=W)

    contract_add_input_public = ttk.Entry(bottom_frame, width=90, justify='center', font=("DejaVu Sans Mono", 13))

    contract_add_input_public.grid(row=5, column=1)

    contract_add_label_private = ttk.Label(bottom_frame, text="Enter private hash of your account(optional): ", font=("Ariel, 20"), justify='left')

    contract_add_label_private.grid(row=6, column=0, pady=20, padx=20, sticky=W)

    contract_add_input_private = ttk.Entry(bottom_frame, width=90, justify='center', font=("DejaVu Sans Mono", 13), show='*')

    contract_add_input_private.grid(row=6, column=1)

    button_style = ttk.Style()
    button_style.configure('W.TButton', font= ('Arial', 17))

    submit_contract = ttk.Button(bottom_frame, text="Connect", width=30, style='W.TButton', command=lambda: show_contract_details(bottom_frame, public_hash=contract_add_input_public.get().strip(), private_hash=contract_add_input_private.get().strip()), )

    submit_contract.grid(row=7, columnspan=2,  pady=20)

    bottom_frame.grid(row=5, column=0)


def connect_wallet():
    global pytezos_inst, network_url, wallet_address
    wallet_address = welcome_input.get().strip()
    network_choice = network_dropdown.get().strip()

    if(len(wallet_address) == 0):
        show_warning(window, 2000, "Wallet address can't be emtpy!")
        return
    
    if(wallet_address.isalnum() and len(wallet_address) == 36):
        try:
            
            pytezos_inst =  pytezos.using(shell=f"https://rpc.tzkt.io/{network_choice}", key=wallet_address)
            network_url = f"https://rpc.tzkt.io/{network_choice}"

            clear_contents(root_top_frame)
            clear_contents(root_bottom_frame)
            create_wallet_screen(wallet_address=wallet_address, network=network_choice)

        except:
            
            show_warning(window, 3000, "Unable to connect the wallet with tezos... try again later")
    else:
        show_warning(window, 3000, "Invalid key address entered!")

    return

# ------------------------

# widgets -------------------

logo_path = __file__.replace("main.py", "pytezos_logo.png")

image = ImageTk.PhotoImage(Image.open(logo_path).resize((200,200)))

img_label = Label(root_top_frame, image=image)

img_label.grid(row=0, column=0, padx=((window_width/2)-800,0), pady=20)

welcome_heading = ttk.Label(root_top_frame, text="PyTezos", font=("Ariel", 150, "bold italic"))
welcome_heading.grid(row=0, column=1, pady=20)

root_top_frame.grid()

root_bottom_frame = Frame(window)

wallet_address_label = ttk.Label(root_bottom_frame, text="Enter your wallet address here: ", font=("Ariel", 28))
wallet_address_label.grid(row=1, column=0, padx=(200,0))

welcome_input = ttk.Entry(root_bottom_frame, width=90, justify='center', font=("DejaVu Sans Mono", 13))
welcome_input.grid(row=1, column=1, pady=20)

welcome_input.focus()

wallet_address_label = ttk.Label(root_bottom_frame, text="Enter the network: ", font=("Ariel, 28"), justify='left')
wallet_address_label.grid(sticky=W, row=2, column=0, padx=(200,0))

choice = IntVar(window)
choice.set("mainnet")
network_dropdown = ttk.Spinbox(root_bottom_frame, values=('ghostnet', 'limanet', 'mainnet'), font=("Ariel", 13, "bold"), state='readonly', textvariable=choice,width=50, )
network_dropdown.grid(row=2, column=1, pady=20)


button_style = Style()
button_style.configure('W.TButton', font= ('Arial', 17))

connect_wallet_button = ttk.Button(root_bottom_frame, text="Connect Wallet", width=30, command=connect_wallet, style='W.TButton')
connect_wallet_button.grid(row=3, columnspan=2, pady=100, padx=200)

root_bottom_frame.grid()
# -------------------------

window.mainloop()