<script>
    import { getContext, onMount } from "svelte";
    import NeedsAuthorisation from "$lib/components/NeedsAuthorisation.svelte";
    import AppointmentDashboard from "$lib/components/AppointmentDashboard.svelte";
    import PrescriptionTable from "$lib/components/PrescriptionTable.svelte";
    import UserTable from "$lib/components/UserTable.svelte";

    const session = getContext("session");
    let doctorTypes = [0,1,2,3]
    let userId = $session.userId;
</script>

<NeedsAuthorisation userType={$session.userType} userTypesPermitted={[0, 1, 2, 3, 5]} />

<h1> Dashboard </h1>

{#if $session.userType === 5}
<!-- USER DASHBOARD -->
<AppointmentDashboard title="Outstanding Appointments" stage_id=012></AppointmentDashboard>
<br>
<AppointmentDashboard title="Past Appointments" stage_id=34></AppointmentDashboard>
<br>
<PrescriptionTable session={session} is_doctor={doctorTypes.includes($session.userType)} />

{:else if [2, 3].includes($session.userType)}
<!-- STAFF DASHBOARD-->
<AppointmentDashboard title="Appointments For Today" staff_id={userId} stage_id=2 today_only=true></AppointmentDashboard>
<br>
<AppointmentDashboard title="Assigned To Me" staff_id={userId}, stage_id=2></AppointmentDashboard>
<br>
<AppointmentDashboard title="Waiting For Approval" stage_id=0></AppointmentDashboard>
<br>
<AppointmentDashboard title="Requires Manual Scheduling" stage_id=1></AppointmentDashboard>
<br>
<PrescriptionTable session={session} is_doctor={doctorTypes.includes($session.userType)} />

{:else if [0, 1].includes($session.userType)}
<!-- ADMIN DASHBOARD -->
<UserTable userTypes={[2, 3]} title="Unactivated Staff Users" filters={["is_active=false"]} />

{/if}